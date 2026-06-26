"""
=============================================================================
SIMULACION DEL ESCENARIO MEJORADO CON DSS
=============================================================================
Aplica las reglas del sistema de apoyo a la decision sobre el escenario base
y genera un escenario mejorado para comparacion de KPIs.

Modulos del DSS simulados:
  M1. Asignacion inteligente de muelles (reglas de compatibilidad + ocupacion)
  M2. Priorizacion efectiva (cola de espera con reglas de prioridad)
  M3. Gestion dinamica de recursos (reasignacion proactiva de gruas)
  M4. Anticipacion de cuellos de botella (holgura entre escalas)
  M5. Alertas y prevencion de cascadas (deteccion de picos)
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

RUTA = '/Users/javierlopezgil/Desktop/TFG_Portuario/datos/'
RUTA_FIG = '/Users/javierlopezgil/Desktop/TFG_Portuario/figuras/'

# ============================================================================
# CARGA DE DATOS DEL ESCENARIO BASE
# ============================================================================
muelles = pd.read_csv(RUTA + '01_muelles.csv')
recursos = pd.read_csv(RUTA + '02_recursos.csv')
buques = pd.read_csv(RUTA + '03_buques.csv')
escalas_base = pd.read_csv(RUTA + '04_escalas.csv')
incidencias_base = pd.read_csv(RUTA + '05_incidencias.csv')
asignaciones_base = pd.read_csv(RUTA + '06_asignacion_recursos.csv')

for col in ['eta', 'ata', 'hora_inicio_op', 'hora_fin_op']:
    escalas_base[col] = pd.to_datetime(escalas_base[col])

escalas_base = escalas_base.merge(
    buques[['id_buque', 'tipo_buque', 'eslora_m', 'calado_m']], on='id_buque'
)

HORAS_PERIODO = 91 * 24
nombres_muelles = dict(zip(muelles['id_muelle'], muelles['nombre_muelle']))

# ============================================================================
# COMPATIBILIDAD DE CARGA
# ============================================================================
COMPAT_PRIMARIA = {
    'granel solido':  [1, 3, 4],
    'granel liquido': [4],
    'carga general':  [1, 2, 3, 5],
    'contenedores':   [2],
    'carga rodada':   [5],
}

# Compatibilidad extendida: muelles secundarios aceptables bajo DSS
# El DSS permite derivar ciertos tipos a muelles alternativos si hay holgura
COMPAT_SECUNDARIA = {
    'granel solido':  [2],        # Muelle Sur puede recibir granel solido con grua movil
    'carga general':  [],         # Ya tiene buena cobertura
    'contenedores':   [1, 3],     # Con grua movil, se pueden operar en Norte o Este
    'carga rodada':   [2],        # En emergencia, carga rodada en Muelle Sur
    'granel liquido': [],         # Sin alternativa (requiere bombeo)
}

# Muelle preferente (optimo) por tipo de carga
MUELLE_PREFERENTE = {
    'granel solido':  [1, 4],     # Norte y Oeste (con grua fija o cinta)
    'granel liquido': [4],
    'carga general':  [2, 1],     # Sur preferente, luego Norte
    'contenedores':   [2],
    'carga rodada':   [5],
}

# ============================================================================
# REGLAS DEL DSS
# ============================================================================

def calcular_prioridad_efectiva(row, ocupacion_muelles, hora_actual):
    """
    MODULO M2: Calcula una puntuacion de prioridad numerica que integra:
    - Prioridad asignada (alta=3, media=2, baja=1)
    - Tiempo ya en espera (mas espera = mas urgencia)
    - Tipo de buque (tanques y portacontenedores con ligera bonificacion
      por coste de demora mas alto)
    - Penalizacion por ventana de atraque proxima a expirar
    """
    # Base por prioridad declarada
    base = {'alta': 30, 'media': 15, 'baja': 5}
    score = base.get(row['prioridad'], 10)

    # Bonificacion por tiempo en espera (1 punto por hora de espera acumulada)
    tiempo_esperando = max(0, (hora_actual - row['ata']).total_seconds() / 3600)
    score += tiempo_esperando * 1.5

    # Bonificacion por tipo de buque (coste de demora)
    bonif_tipo = {'tanque': 8, 'portacontenedores': 6, 'granelero': 3,
                  'carga general': 2, 'ro-ro': 4}
    score += bonif_tipo.get(row['tipo_buque'], 0)

    # Penalizacion si ya lleva mas de 6h esperando (urgencia)
    if tiempo_esperando > 6:
        score += 15
    elif tiempo_esperando > 3:
        score += 8

    return score


def seleccionar_muelle_dss(row, ocupacion_muelles, hora_actual, muelles_df):
    """
    MODULO M1: Asignacion inteligente de muelles.

    Logica:
    1. Buscar muelle preferente disponible y compatible
    2. Si no hay, buscar muelle primario compatible (no preferente)
    3. Si no hay, buscar muelle secundario compatible (con penalizacion aceptable)
    4. Si no hay nada libre, calcular cual se libera antes y estimar espera

    Diferencia con escenario base:
    - Considera ocupacion prevista (no solo actual)
    - Amplia opciones de asignacion cuando hay congestion
    - Introduce holgura de 45 min entre escalas (MODULO M4)
    """
    tipo_carga = row['tipo_carga']
    eslora = row['eslora_m']
    calado = row['calado_m']

    HOLGURA = timedelta(minutes=45)  # Buffer entre escalas

    def es_fisicamente_compatible(m_id):
        m = muelles_df[muelles_df['id_muelle'] == m_id].iloc[0]
        return eslora <= m['longitud_m'] and calado <= m['calado_max_m']

    def esta_disponible(m_id, hora):
        if m_id not in ocupacion_muelles:
            return True
        return ocupacion_muelles[m_id] + HOLGURA <= hora

    def hora_liberacion(m_id):
        if m_id not in ocupacion_muelles:
            return hora_actual
        return ocupacion_muelles[m_id] + HOLGURA

    # Paso 1: Muelle preferente disponible
    preferentes = MUELLE_PREFERENTE.get(tipo_carga, [])
    for m_id in preferentes:
        if es_fisicamente_compatible(m_id) and esta_disponible(m_id, hora_actual):
            return m_id, 'preferente', 0

    # Paso 2: Muelle primario compatible disponible
    primarios = COMPAT_PRIMARIA.get(tipo_carga, [])
    for m_id in primarios:
        if m_id in preferentes:
            continue
        if es_fisicamente_compatible(m_id) and esta_disponible(m_id, hora_actual):
            return m_id, 'primario', 0

    # Paso 3: Muelle secundario compatible disponible (DSS amplía opciones)
    secundarios = COMPAT_SECUNDARIA.get(tipo_carga, [])
    for m_id in secundarios:
        if es_fisicamente_compatible(m_id) and esta_disponible(m_id, hora_actual):
            return m_id, 'secundario', 0

    # Paso 4: Ningun muelle libre. Buscar el que se libera antes.
    todos_compatibles = list(set(preferentes + primarios + secundarios))
    if not todos_compatibles:
        todos_compatibles = primarios if primarios else list(range(1, 6))

    mejor_muelle = None
    menor_espera = float('inf')
    mejor_tipo = 'emergencia'

    for m_id in todos_compatibles:
        if not es_fisicamente_compatible(m_id):
            continue
        lib = hora_liberacion(m_id)
        espera = max(0, (lib - hora_actual).total_seconds() / 3600)
        if espera < menor_espera:
            menor_espera = espera
            mejor_muelle = m_id
            if m_id in preferentes:
                mejor_tipo = 'preferente_espera'
            elif m_id in primarios:
                mejor_tipo = 'primario_espera'
            else:
                mejor_tipo = 'secundario_espera'

    # Fallback absoluto
    if mejor_muelle is None:
        for m_id in range(1, 6):
            if es_fisicamente_compatible(m_id):
                lib = hora_liberacion(m_id)
                espera = max(0, (lib - hora_actual).total_seconds() / 3600)
                if espera < menor_espera:
                    menor_espera = espera
                    mejor_muelle = m_id
                    mejor_tipo = 'emergencia'

    if mejor_muelle is None:
        mejor_muelle = 1
        menor_espera = 12

    return mejor_muelle, mejor_tipo, menor_espera


def calcular_servicio_dss(row, tipo_asignacion, n_gruas_dss):
    """
    MODULO M3: Ajusta el tiempo de servicio considerando:
    - Asignacion optimizada de gruas (reasignacion proactiva)
    - Penalizacion reducida por asignacion secundaria (DSS prepara equipo)
    - Mejora general por coordinacion anticipada (reduccion 5-10%)
    """
    servicio_base = row['tiempo_servicio_h']

    # Mejora por coordinacion anticipada (DSS preavisa recursos)
    factor_coordinacion = np.random.uniform(0.90, 0.97)

    # Mejora por gruas adicionales reasignadas
    if n_gruas_dss > 1 and row['tipo_buque'] in ['granelero', 'carga general', 'portacontenedores']:
        factor_gruas = np.random.uniform(0.80, 0.90)  # 10-20% mejora
    else:
        factor_gruas = 1.0

    # Penalizacion por muelle secundario (menor que en base: DSS prepara equipo)
    if tipo_asignacion == 'secundario' or tipo_asignacion == 'secundario_espera':
        factor_suboptimo = np.random.uniform(1.03, 1.10)  # Solo 3-10% vs 10-25% base
    else:
        factor_suboptimo = 1.0

    servicio_dss = servicio_base * factor_coordinacion * factor_gruas * factor_suboptimo
    return round(max(servicio_dss, 2), 2)


def tiene_incidencia_base(id_escala, incidencias_df):
    """Verifica si la escala tiene incidencia en el escenario base."""
    return id_escala in incidencias_df['id_escala'].values


def reducir_incidencia_dss(id_escala, incidencias_df):
    """
    MODULO M5: El DSS no elimina incidencias externas (meteo, averias),
    pero reduce el impacto de incidencias de coordinacion y gestion.
    """
    inc = incidencias_df[incidencias_df['id_escala'] == id_escala]
    if inc.empty:
        return 0

    reduccion_total = 0
    for _, i in inc.iterrows():
        tipo = i['tipo_incidencia']
        dur = i['duracion_h']

        if tipo in ['fallo de coordinacion', 'problema documental o administrativo']:
            # DSS reduce 60-80% del impacto por anticipacion
            reduccion_total += dur * np.random.uniform(0.60, 0.80)
        elif tipo in ['indisponibilidad de recurso por turno', 'falta de personal']:
            # DSS reduce 40-60% por planificacion anticipada de turnos
            reduccion_total += dur * np.random.uniform(0.40, 0.60)
        elif tipo == 'congestion de muelle':
            # DSS reduce 50-70% por mejor secuenciacion
            reduccion_total += dur * np.random.uniform(0.50, 0.70)
        elif tipo in ['averia de equipo', 'condiciones meteorologicas adversas']:
            # DSS no puede evitarlas pero alerta antes: 10-20% reduccion
            reduccion_total += dur * np.random.uniform(0.10, 0.20)
        else:
            reduccion_total += dur * np.random.uniform(0.10, 0.30)

    return round(reduccion_total, 2)


# ============================================================================
# SIMULACION DEL ESCENARIO MEJORADO
# ============================================================================
print("=" * 80)
print("SIMULACION DEL ESCENARIO MEJORADO CON DSS")
print("=" * 80)

# Ordenar escalas por ATA (llegada real) y luego por prioridad efectiva
escalas_dss = escalas_base.copy()
escalas_dss = escalas_dss.sort_values('ata').reset_index(drop=True)

# Control de ocupacion de muelles (DSS)
ocupacion_muelles_dss = {}

# Resultados
resultados_dss = []

# Cola de buques esperando (para priorizacion)
# Procesamos por bloques temporales (ventanas de 2 horas)
escalas_dss['ventana'] = escalas_dss['ata'].dt.floor('2h')

for ventana, grupo in escalas_dss.groupby('ventana'):
    # Dentro de cada ventana, ordenar por prioridad efectiva
    grupo = grupo.copy()
    grupo['score_prioridad'] = grupo.apply(
        lambda r: calcular_prioridad_efectiva(r, ocupacion_muelles_dss, r['ata']),
        axis=1
    )
    grupo = grupo.sort_values('score_prioridad', ascending=False)

    for _, row in grupo.iterrows():
        # M1: Asignacion inteligente de muelle
        muelle_id, tipo_asig, espera_muelle = seleccionar_muelle_dss(
            row, ocupacion_muelles_dss, row['ata'], muelles
        )

        # Calcular tiempo de espera DSS
        espera_base = espera_muelle  # Espera por disponibilidad de muelle

        # Espera adicional por meteorologia (no controlable)
        espera_meteo = 0
        if row['causa_espera'] == 'condiciones meteorologicas adversas':
            # DSS no puede evitar la meteo pero anticipa: reduce 15-25%
            espera_meteo_base = min(row['tiempo_espera_h'], 12)
            espera_meteo = espera_meteo_base * np.random.uniform(0.75, 0.85)

        # Espera por practicaje (DSS coordina con anticipacion: reduce 50-70%)
        espera_practicaje = 0
        if row['causa_espera'] == 'espera de practicaje':
            espera_practicaje = min(row['tiempo_espera_h'], 3) * np.random.uniform(0.30, 0.50)

        # Espera documental (DSS digitaliza tramites: reduce 60-80%)
        espera_documental = 0
        if row['causa_espera'] == 'espera documental / despacho':
            espera_documental = min(row['tiempo_espera_h'], 2) * np.random.uniform(0.20, 0.40)

        # Espera minima operativa (maniobra previa)
        espera_minima = np.random.uniform(0.1, 0.4)

        tiempo_espera_dss = max(espera_minima, espera_base + espera_meteo +
                                espera_practicaje + espera_documental)

        # Cap maximo (si DSS detecta espera > 30h, propone desvio - no ocurre aqui)
        tiempo_espera_dss = min(tiempo_espera_dss, 30)
        tiempo_espera_dss = round(tiempo_espera_dss, 2)

        # Hora de inicio de operacion DSS
        hora_inicio_dss = row['ata'] + timedelta(hours=tiempo_espera_dss)

        # M3: Gestion dinamica de recursos (mas gruas si hay disponibilidad)
        n_gruas_dss = 1
        if row['tipo_buque'] in ['granelero', 'carga general', 'portacontenedores']:
            if row['volumen_carga_t'] > 12000:
                n_gruas_dss = 2
            elif row['volumen_carga_t'] > 8000 and np.random.random() < 0.5:
                n_gruas_dss = 2

        # M3 + M5: Tiempo de servicio mejorado
        tiempo_servicio_dss = calcular_servicio_dss(row, tipo_asig, n_gruas_dss)

        # Reduccion por mitigacion de incidencias
        reduccion_inc = reducir_incidencia_dss(row['id_escala'], incidencias_base)
        tiempo_servicio_dss = max(2, tiempo_servicio_dss - reduccion_inc * 0.5)
        tiempo_servicio_dss = round(tiempo_servicio_dss, 2)

        # Hora de fin y tiempos totales
        hora_fin_dss = hora_inicio_dss + timedelta(hours=tiempo_servicio_dss)
        tiempo_total_dss = round(tiempo_espera_dss + tiempo_servicio_dss, 2)

        # Actualizar ocupacion del muelle DSS
        ocupacion_muelles_dss[muelle_id] = hora_fin_dss

        # Determinar causa de espera DSS
        if tiempo_espera_dss <= 0.5:
            causa_dss = 'sin espera significativa'
        elif espera_muelle > 0.5:
            causa_dss = 'muelle ocupado (gestionado por DSS)'
        elif espera_meteo > 0:
            causa_dss = 'condiciones meteorologicas (parcialmente mitigado)'
        elif espera_practicaje > 0:
            causa_dss = 'practicaje (coordinado por DSS)'
        else:
            causa_dss = 'espera operativa menor'

        # Es asignacion optima?
        muelles_ideales = COMPAT_PRIMARIA.get(row['tipo_carga'], [])
        es_compatible = muelle_id in muelles_ideales

        resultados_dss.append({
            'id_escala': row['id_escala'],
            'id_buque': row['id_buque'],
            'tipo_buque': row['tipo_buque'],
            'id_muelle_base': row['id_muelle'],
            'id_muelle_dss': muelle_id,
            'tipo_asignacion': tipo_asig,
            'tipo_carga': row['tipo_carga'],
            'volumen_carga_t': row['volumen_carga_t'],
            'prioridad': row['prioridad'],
            'ata': row['ata'],
            'tiempo_espera_base': row['tiempo_espera_h'],
            'tiempo_espera_dss': tiempo_espera_dss,
            'tiempo_servicio_base': row['tiempo_servicio_h'],
            'tiempo_servicio_dss': tiempo_servicio_dss,
            'tiempo_total_base': row['tiempo_total_h'],
            'tiempo_total_dss': tiempo_total_dss,
            'causa_espera_base': row['causa_espera'],
            'causa_espera_dss': causa_dss,
            'n_gruas_dss': n_gruas_dss,
            'compatible_muelle': es_compatible,
            'cambio_muelle': row['id_muelle'] != muelle_id,
        })

df_dss = pd.DataFrame(resultados_dss)

# ============================================================================
# COMPARACION DE KPIs: BASE vs DSS
# ============================================================================
print("\n" + "=" * 80)
print("COMPARACION DE KPIs: ESCENARIO BASE vs ESCENARIO DSS")
print("=" * 80)

def pct_cambio(base, dss):
    if base == 0:
        return 0
    return ((dss - base) / base) * 100

# --- TIEMPOS ---
awt_base = df_dss['tiempo_espera_base'].mean()
awt_dss = df_dss['tiempo_espera_dss'].mean()
med_base = df_dss['tiempo_espera_base'].median()
med_dss = df_dss['tiempo_espera_dss'].median()
ast_base = df_dss['tiempo_servicio_base'].mean()
ast_dss = df_dss['tiempo_servicio_dss'].mean()
att_base = df_dss['tiempo_total_base'].mean()
att_dss = df_dss['tiempo_total_dss'].mean()
wtr_base = awt_base / ast_base
wtr_dss = awt_dss / ast_dss

pct6h_base = (df_dss['tiempo_espera_base'] > 6).mean() * 100
pct6h_dss = (df_dss['tiempo_espera_dss'] > 6).mean() * 100
pct24h_base = (df_dss['tiempo_espera_base'] > 24).mean() * 100
pct24h_dss = (df_dss['tiempo_espera_dss'] > 24).mean() * 100

print("\n--- KPIs DE TIEMPO ---")
print(f"{'KPI':40s} {'Base':>10s} {'DSS':>10s} {'Cambio':>10s}")
print("-" * 75)
print(f"{'AWT (media)':40s} {awt_base:>9.2f}h {awt_dss:>9.2f}h {pct_cambio(awt_base, awt_dss):>+9.1f}%")
print(f"{'AWT (mediana)':40s} {med_base:>9.2f}h {med_dss:>9.2f}h {pct_cambio(med_base, med_dss):>+9.1f}%")
print(f"{'AST (media)':40s} {ast_base:>9.2f}h {ast_dss:>9.2f}h {pct_cambio(ast_base, ast_dss):>+9.1f}%")
print(f"{'ATT (media)':40s} {att_base:>9.2f}h {att_dss:>9.2f}h {pct_cambio(att_base, att_dss):>+9.1f}%")
print(f"{'WTR':40s} {wtr_base:>9.3f}  {wtr_dss:>9.3f}  {pct_cambio(wtr_base, wtr_dss):>+9.1f}%")
print(f"{'% espera > 6h':40s} {pct6h_base:>8.1f}%  {pct6h_dss:>8.1f}%  {pct_cambio(pct6h_base, pct6h_dss):>+9.1f}%")
print(f"{'% espera > 24h':40s} {pct24h_base:>8.1f}%  {pct24h_dss:>8.1f}%  {pct_cambio(pct24h_base, pct24h_dss):>+9.1f}%")

# --- Por tipo de buque ---
print("\n--- ESPERA MEDIA POR TIPO DE BUQUE ---")
print(f"{'Tipo':20s} {'Base':>10s} {'DSS':>10s} {'Cambio':>10s}")
print("-" * 55)
for tipo in ['granelero', 'carga general', 'tanque', 'portacontenedores', 'ro-ro']:
    sub = df_dss[df_dss['tipo_buque'] == tipo]
    eb = sub['tiempo_espera_base'].mean()
    ed = sub['tiempo_espera_dss'].mean()
    print(f"{tipo:20s} {eb:>9.2f}h {ed:>9.2f}h {pct_cambio(eb, ed):>+9.1f}%")

# --- Por prioridad ---
print("\n--- ESPERA MEDIA POR PRIORIDAD ---")
print(f"{'Prioridad':20s} {'Base':>10s} {'DSS':>10s} {'Cambio':>10s}")
print("-" * 55)
for prio in ['alta', 'media', 'baja']:
    sub = df_dss[df_dss['prioridad'] == prio]
    eb = sub['tiempo_espera_base'].mean()
    ed = sub['tiempo_espera_dss'].mean()
    print(f"{prio:20s} {eb:>9.2f}h {ed:>9.2f}h {pct_cambio(eb, ed):>+9.1f}%")

# --- BOR por muelle DSS ---
print("\n--- BOR POR MUELLE ---")
print(f"{'Muelle':20s} {'Esc.Base':>10s} {'BOR Base':>10s} {'Esc.DSS':>10s} {'BOR DSS':>10s}")
print("-" * 65)
for m_id in range(1, 6):
    n_base = (df_dss['id_muelle_base'] == m_id).sum()
    serv_base = df_dss[df_dss['id_muelle_base'] == m_id]['tiempo_servicio_base'].sum()
    bor_b = serv_base / HORAS_PERIODO * 100

    n_dss = (df_dss['id_muelle_dss'] == m_id).sum()
    serv_dss = df_dss[df_dss['id_muelle_dss'] == m_id]['tiempo_servicio_dss'].sum()
    bor_d = serv_dss / HORAS_PERIODO * 100

    nombre = nombres_muelles[m_id]
    print(f"{nombre:20s} {n_base:>10d} {bor_b:>9.1f}% {n_dss:>10d} {bor_d:>9.1f}%")

# --- Compatibilidad ---
compat_base_pct = (df_dss['id_muelle_base'].apply(
    lambda m: m in COMPAT_PRIMARIA.get(df_dss.loc[df_dss.index[0], 'tipo_carga'], [])
)).mean() * 100  # This is wrong, fix below

# Recalculate properly
compat_base = 0
compat_dss = 0
for _, row in df_dss.iterrows():
    ideales = COMPAT_PRIMARIA.get(row['tipo_carga'], [])
    if row['id_muelle_base'] in ideales:
        compat_base += 1
    if row['id_muelle_dss'] in ideales:
        compat_dss += 1

print(f"\nCompatibilidad buque-muelle: Base={compat_base/len(df_dss)*100:.1f}% | DSS={compat_dss/len(df_dss)*100:.1f}%")
print(f"Escalas reasignadas a otro muelle: {df_dss['cambio_muelle'].sum()} ({df_dss['cambio_muelle'].mean()*100:.1f}%)")

# --- Cuellos de botella DSS ---
df_dss['fecha'] = df_dss['ata'].dt.date
dias_cuello_base = 0
dias_cuello_dss = 0
for fecha in df_dss['fecha'].unique():
    sub = df_dss[df_dss['fecha'] == fecha]
    if (sub['tiempo_espera_base'] > 4).sum() >= 2:
        dias_cuello_base += 1
    if (sub['tiempo_espera_dss'] > 4).sum() >= 2:
        dias_cuello_dss += 1

print(f"\nDias con cuello de botella: Base={dias_cuello_base} | DSS={dias_cuello_dss} ({pct_cambio(dias_cuello_base, dias_cuello_dss):+.1f}%)")

# Indice propagacion
prop_base = (df_dss['tiempo_espera_base'] > 4).sum()
prop_dss = (df_dss['tiempo_espera_dss'] > 4).sum()
print(f"Escalas con espera > 4h: Base={prop_base} | DSS={prop_dss} ({pct_cambio(prop_base, prop_dss):+.1f}%)")

# ============================================================================
# TABLA RESUMEN COMPARATIVA
# ============================================================================
print("\n" + "=" * 80)
print("TABLA RESUMEN COMPARATIVA")
print("=" * 80)

resumen = pd.DataFrame({
    'KPI': [
        'Tiempo medio de espera (AWT)',
        'Mediana de espera',
        'Tiempo medio de servicio (AST)',
        'Tiempo medio de estancia (ATT)',
        'Ratio de espera (WTR)',
        '% escalas espera > 6h',
        '% escalas espera > 24h',
        'Dias con cuello de botella',
        'Escalas con espera > 4h',
    ],
    'Escenario Base': [
        f'{awt_base:.2f} h', f'{med_base:.2f} h', f'{ast_base:.2f} h',
        f'{att_base:.2f} h', f'{wtr_base:.3f}', f'{pct6h_base:.1f}%',
        f'{pct24h_base:.1f}%', str(dias_cuello_base), str(prop_base),
    ],
    'Escenario DSS': [
        f'{awt_dss:.2f} h', f'{med_dss:.2f} h', f'{ast_dss:.2f} h',
        f'{att_dss:.2f} h', f'{wtr_dss:.3f}', f'{pct6h_dss:.1f}%',
        f'{pct24h_dss:.1f}%', str(dias_cuello_dss), str(prop_dss),
    ],
    'Variacion': [
        f'{pct_cambio(awt_base, awt_dss):+.1f}%',
        f'{pct_cambio(med_base, med_dss):+.1f}%',
        f'{pct_cambio(ast_base, ast_dss):+.1f}%',
        f'{pct_cambio(att_base, att_dss):+.1f}%',
        f'{pct_cambio(wtr_base, wtr_dss):+.1f}%',
        f'{pct_cambio(pct6h_base, pct6h_dss):+.1f}%',
        f'{pct_cambio(pct24h_base, pct24h_dss):+.1f}%',
        f'{pct_cambio(dias_cuello_base, dias_cuello_dss):+.1f}%',
        f'{pct_cambio(prop_base, prop_dss):+.1f}%',
    ]
})
print(resumen.to_string(index=False))
resumen.to_csv(RUTA + 'KPIs_comparativa_base_dss.csv', index=False, encoding='utf-8-sig')

# ============================================================================
# GRAFICOS COMPARATIVOS
# ============================================================================
print("\n\nGenerando graficos comparativos...")

# --- Fig 9: Comparacion de esperas base vs DSS ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(df_dss['tiempo_espera_base'], bins=25, alpha=0.6, color='#e74c3c',
             edgecolor='black', label=f'Base (media={awt_base:.1f}h)')
axes[0].hist(df_dss['tiempo_espera_dss'], bins=25, alpha=0.6, color='#27ae60',
             edgecolor='black', label=f'DSS (media={awt_dss:.1f}h)')
axes[0].set_xlabel('Tiempo de espera (horas)')
axes[0].set_ylabel('Frecuencia')
axes[0].set_title('Distribución de tiempos de espera: Base vs DSS')
axes[0].legend()

# Scatter base vs DSS
axes[1].scatter(df_dss['tiempo_espera_base'], df_dss['tiempo_espera_dss'],
                alpha=0.5, s=30, c='#3498db')
max_val = max(df_dss['tiempo_espera_base'].max(), df_dss['tiempo_espera_dss'].max())
axes[1].plot([0, max_val], [0, max_val], 'k--', alpha=0.3, label='Sin cambio')
axes[1].set_xlabel('Espera Base (h)')
axes[1].set_ylabel('Espera DSS (h)')
axes[1].set_title('Espera Base vs DSS (por escala)')
axes[1].legend()
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig09_comparacion_esperas.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 10: Comparacion KPIs principales (barras) ---
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# AWT por tipo
tipos = ['granelero', 'carga general', 'tanque', 'portacontenedores', 'ro-ro']
awt_base_tipo = [df_dss[df_dss['tipo_buque']==t]['tiempo_espera_base'].mean() for t in tipos]
awt_dss_tipo = [df_dss[df_dss['tipo_buque']==t]['tiempo_espera_dss'].mean() for t in tipos]
x = np.arange(len(tipos))
w = 0.35
axes[0].bar(x - w/2, awt_base_tipo, w, label='Base', color='#e74c3c', alpha=0.7)
axes[0].bar(x + w/2, awt_dss_tipo, w, label='DSS', color='#27ae60', alpha=0.7)
axes[0].set_xticks(x)
axes[0].set_xticklabels([t.replace(' ', '\n') for t in tipos], fontsize=9)
axes[0].set_ylabel('Espera media (h)')
axes[0].set_title('Espera media por tipo de buque')
axes[0].legend()

# AWT por prioridad
prios = ['alta', 'media', 'baja']
awt_base_prio = [df_dss[df_dss['prioridad']==p]['tiempo_espera_base'].mean() for p in prios]
awt_dss_prio = [df_dss[df_dss['prioridad']==p]['tiempo_espera_dss'].mean() for p in prios]
x2 = np.arange(len(prios))
axes[1].bar(x2 - w/2, awt_base_prio, w, label='Base', color='#e74c3c', alpha=0.7)
axes[1].bar(x2 + w/2, awt_dss_prio, w, label='DSS', color='#27ae60', alpha=0.7)
axes[1].set_xticks(x2)
axes[1].set_xticklabels(prios)
axes[1].set_ylabel('Espera media (h)')
axes[1].set_title('Espera media por prioridad')
axes[1].legend()

# BOR por muelle
bor_base_m = []
bor_dss_m = []
for m_id in range(1, 6):
    sb = df_dss[df_dss['id_muelle_base'] == m_id]['tiempo_servicio_base'].sum() / HORAS_PERIODO * 100
    sd = df_dss[df_dss['id_muelle_dss'] == m_id]['tiempo_servicio_dss'].sum() / HORAS_PERIODO * 100
    bor_base_m.append(sb)
    bor_dss_m.append(sd)
x3 = np.arange(5)
axes[2].bar(x3 - w/2, bor_base_m, w, label='Base', color='#e74c3c', alpha=0.7)
axes[2].bar(x3 + w/2, bor_dss_m, w, label='DSS', color='#27ae60', alpha=0.7)
axes[2].axhline(65, color='red', linestyle='--', alpha=0.5, label='Umbral 65%')
axes[2].set_xticks(x3)
axes[2].set_xticklabels(['Norte','Sur','Este','Oeste','Ro-Ro'], fontsize=9)
axes[2].set_ylabel('BOR (%)')
axes[2].set_title('Ocupación de muelles (BOR)')
axes[2].legend(fontsize=8)
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig10_comparacion_kpis.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 11: Mejora porcentual por KPI ---
fig, ax = plt.subplots(figsize=(10, 6))
kpis_mejora = {
    'Tiempo medio\nde espera': pct_cambio(awt_base, awt_dss),
    'Esperas\n> 6 horas': pct_cambio(pct6h_base, pct6h_dss),
    'Esperas\n> 24 horas': pct_cambio(pct24h_base, pct24h_dss),
    'Ratio de\nespera (WTR)': pct_cambio(wtr_base, wtr_dss),
    'Tiempo medio\nde servicio': pct_cambio(ast_base, ast_dss),
    'Tiempo medio\ntotal': pct_cambio(att_base, att_dss),
    'Dias con\ncuello botella': pct_cambio(dias_cuello_base, dias_cuello_dss),
    'Escalas con\nespera > 4h': pct_cambio(prop_base, prop_dss),
}
nombres_k = list(kpis_mejora.keys())
valores_k = list(kpis_mejora.values())
colores = ['#27ae60' if v < 0 else '#e74c3c' for v in valores_k]
bars = ax.barh(nombres_k, valores_k, color=colores, edgecolor='black', alpha=0.8)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('Variación porcentual (%)')
ax.set_title('Impacto del DSS: variación porcentual respecto al escenario base')
for bar, val in zip(bars, valores_k):
    ax.text(bar.get_width() + (1 if val < 0 else -1), bar.get_y() + bar.get_height()/2,
            f'{val:+.1f}%', va='center', ha='left' if val < 0 else 'right', fontweight='bold')
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig11_impacto_dss.png', dpi=150, bbox_inches='tight')
plt.close()

# Guardar dataset DSS
df_dss.to_csv(RUTA + '07_escenario_dss.csv', index=False, encoding='utf-8-sig')

print(f"\nArchivos generados:")
print(f"  {RUTA}07_escenario_dss.csv")
print(f"  {RUTA}KPIs_comparativa_base_dss.csv")
print(f"  {RUTA_FIG}fig09_comparacion_esperas.png")
print(f"  {RUTA_FIG}fig10_comparacion_kpis.png")
print(f"  {RUTA_FIG}fig11_impacto_dss.png")
print("\n" + "=" * 80)
print("SIMULACION COMPLETADA")
print("=" * 80)
