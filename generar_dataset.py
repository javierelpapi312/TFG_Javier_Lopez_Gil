"""
=============================================================================
GENERADOR DE DATASET SIMULADO - TFG EFICIENCIA OPERATIVA PORTUARIA
=============================================================================
Autor: [Autor del TFG]
Fecha: Marzo 2026

AVISO DE TRANSPARENCIA:
    Todos los datos generados por este script son FICTICIOS.
    Han sido construidos con fines exclusivamente academicos, inspirados
    en patrones operativos plausibles de terminales portuarias polivalentes.
    NO corresponden a registros internos reales de ninguna empresa.

Semilla aleatoria fija (SEED=42) para garantizar reproducibilidad.
=============================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SEMILLA PARA REPRODUCIBILIDAD
# ============================================================================
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# ============================================================================
# PARAMETROS GENERALES
# ============================================================================
FECHA_INICIO = datetime(2025, 9, 1, 0, 0)   # Inicio del periodo simulado
FECHA_FIN = datetime(2025, 11, 30, 23, 59)   # Fin del periodo simulado
NUM_DIAS = (FECHA_FIN - FECHA_INICIO).days + 1  # ~91 dias

# ============================================================================
# TABLA 1: MUELLES
# ============================================================================
def generar_muelles():
    muelles = pd.DataFrame({
        'id_muelle': [1, 2, 3, 4, 5],
        'nombre_muelle': [
            'Muelle Norte', 'Muelle Sur', 'Muelle Este',
            'Muelle Oeste', 'Muelle Ro-Ro'
        ],
        'longitud_m': [250.0, 200.0, 180.0, 220.0, 150.0],
        'calado_max_m': [14.0, 12.0, 10.5, 13.0, 8.0],
        'tipos_carga_admitidos': [
            'granel solido;carga general',
            'carga general;contenedores',
            'granel solido;carga general',
            'granel liquido;granel solido',
            'carga rodada;carga general'
        ],
        'gruas_fijas': [1, 1, 0, 0, 0],
        'estado': ['operativo', 'operativo', 'operativo', 'operativo', 'operativo']
    })
    return muelles

# ============================================================================
# TABLA 2: RECURSOS
# ============================================================================
def generar_recursos():
    recursos = [
        (1,  'grua portico',       'Grua Portico MN-01',       '40 t, 30 mov/h',  'operativo'),
        (2,  'grua portico',       'Grua Portico MS-01',       '35 t, 28 mov/h',  'operativo'),
        (3,  'grua movil',         'Grua Movil GM-01',         '100 t',            'operativo'),
        (4,  'grua movil',         'Grua Movil GM-02',         '80 t',             'operativo'),
        (5,  'grua movil',         'Grua Movil GM-03',         '60 t',             'operativo'),
        (6,  'pala cargadora',     'Pala CAT 980M-01',         '6 m3',             'operativo'),
        (7,  'pala cargadora',     'Pala CAT 980M-02',         '6 m3',             'operativo'),
        (8,  'pala cargadora',     'Pala Komatsu WA-01',       '5 m3',             'operativo'),
        (9,  'cinta transportadora','Cinta CT-01',             '800 t/h',          'operativo'),
        (10, 'cinta transportadora','Cinta CT-02',             '600 t/h',          'operativo'),
        (11, 'tolva',              'Tolva TLV-01',             '30 t',             'operativo'),
        (12, 'tolva',              'Tolva TLV-02',             '30 t',             'operativo'),
        (13, 'carretilla elevadora','Carretilla CE-01',        '5 t',              'operativo'),
        (14, 'carretilla elevadora','Carretilla CE-02',        '5 t',              'operativo'),
        (15, 'carretilla elevadora','Carretilla CE-03',        '3 t',              'operativo'),
        (16, 'reach stacker',      'Reach Stacker RS-01',      '45 t',             'operativo'),
        (17, 'reach stacker',      'Reach Stacker RS-02',      '45 t',             'operativo'),
        (18, 'tractora terminal',  'Tractora TT-01',           '60 t arrastre',    'operativo'),
        (19, 'tractora terminal',  'Tractora TT-02',           '60 t arrastre',    'operativo'),
        (20, 'tractora terminal',  'Tractora TT-03',           '40 t arrastre',    'operativo'),
        (21, 'tractora terminal',  'Tractora TT-04',           '40 t arrastre',    'operativo'),
        (22, 'equipo bombeo',      'Bomba BM-01',              '500 m3/h',         'operativo'),
        (23, 'equipo bombeo',      'Bomba BM-02',              '400 m3/h',         'operativo'),
        (24, 'equipo estiba',      'Equipo Estiba EE-01',      '8 trabajadores',   'operativo'),
        (25, 'equipo estiba',      'Equipo Estiba EE-02',      '8 trabajadores',   'operativo'),
        (26, 'equipo estiba',      'Equipo Estiba EE-03',      '6 trabajadores',   'operativo'),
        (27, 'equipo estiba',      'Equipo Estiba EE-04',      '6 trabajadores',   'operativo'),
    ]
    df = pd.DataFrame(recursos, columns=[
        'id_recurso', 'tipo_recurso', 'nombre_recurso', 'capacidad', 'estado_general'
    ])
    return df

# ============================================================================
# TABLA 3: BUQUES (catalogo)
# ============================================================================

# Nombres ficticios de buques
NOMBRES_BUQUES = [
    'Atlantic Venture', 'Baltic Pioneer', 'Caspian Star', 'Delta Carrier',
    'Europa Spirit', 'Falcon Breeze', 'Gulf Merchant', 'Horizon Trader',
    'Iberian Wave', 'Jade Fortune', 'Kronos Bulk', 'Luna del Sur',
    'Mediterranean Sun', 'Nordic Fjord', 'Oceanus Rex', 'Pacific Horizon',
    'Quasar Tide', 'Rio Bravo', 'Sierra Maestra', 'Titan Express',
    'Ulysses Star', 'Vega Transport', 'Windward Isle', 'Xerxes Glory',
    'Yorktown Bay', 'Zenith Mariner', 'Adriatic Pearl', 'Bosphorus Gate',
    'Coral Stream', 'Danube Spirit', 'Emerald Coast', 'Fortuna Carrier',
    'Gibraltar Passage', 'Hellenic Pride', 'Indigo Voyager', 'Jupiter Cargo',
    'Kestrel Bay', 'Levante Breeze', 'Monsoon Trader', 'Neptune Bulk',
    'Orion Path', 'Poseidon Wave', 'Quantum Freight', 'Rhone Valley',
    'Sahara Wind', 'Tempest Runner', 'Urano Logistics', 'Victoria Harbour',
    'Westerly Gale', 'Zephyr Current', 'Alboran Express', 'Boreal Light',
    'Cyclades Merchant', 'Douro Navigator', 'Estrella del Norte', 'Faro Coast',
    'Galicia Wave', 'Hercules Bulk', 'Isla Bonita', 'Jasper Freight',
    'Kantara Star', 'Lisbon Carrier', 'Mistral Force', 'Navarra Spirit',
    'Olympia Trader', 'Palermo Sun', 'Quixote Venture', 'Roca del Mar',
    'Seville Express', 'Tenerife Breeze', 'Uppsala Cargo', 'Valencia Star',
    'Waterford Tide', 'Xaloc Wind', 'Yamuna Flow', 'Zurich Merchant'
]

BANDERAS = [
    'Panama', 'Liberia', 'Islas Marshall', 'Hong Kong', 'Singapur',
    'Malta', 'Bahamas', 'Grecia', 'Chipre', 'Noruega',
    'España', 'Portugal', 'Italia', 'Paises Bajos', 'Reino Unido',
    'Antigua y Barbuda', 'Turquia', 'Dinamarca'
]

TIPOS_BUQUE = ['granelero', 'carga general', 'tanque', 'ro-ro', 'portacontenedores']
PESOS_TIPO = [0.35, 0.30, 0.15, 0.10, 0.10]

# Parametros por tipo de buque
PARAMS_BUQUE = {
    'granelero': {
        'eslora': (120, 220, 170, 22),
        'calado': (7.0, 13.5),
        'manga': (16, 32),
        'gt': (5000, 45000),
    },
    'carga general': {
        'eslora': (80, 170, 125, 20),
        'calado': (5.0, 10.5),
        'manga': (13, 25),
        'gt': (2000, 20000),
    },
    'tanque': {
        'eslora': (130, 200, 160, 18),
        'calado': (7.5, 12.5),
        'manga': (18, 32),
        'gt': (5000, 40000),
    },
    'ro-ro': {
        'eslora': (100, 180, 140, 18),
        'calado': (5.0, 8.0),
        'manga': (18, 28),
        'gt': (8000, 30000),
    },
    'portacontenedores': {
        'eslora': (130, 200, 165, 18),
        'calado': (7.0, 12.0),
        'manga': (20, 32),
        'gt': (8000, 35000),
    },
}

def generar_buques(n=76):
    """Genera el catalogo de buques ficticios."""
    buques = []
    nombres_usados = random.sample(NOMBRES_BUQUES, min(n, len(NOMBRES_BUQUES)))

    for i in range(n):
        tipo = np.random.choice(TIPOS_BUQUE, p=PESOS_TIPO)
        params = PARAMS_BUQUE[tipo]

        eslora_min, eslora_max, eslora_media, eslora_std = params['eslora']
        eslora = np.clip(np.random.normal(eslora_media, eslora_std), eslora_min, eslora_max)
        eslora = round(eslora, 1)

        # Calado correlacionado con eslora
        calado_min, calado_max = params['calado']
        factor_eslora = (eslora - eslora_min) / (eslora_max - eslora_min)
        calado_base = calado_min + factor_eslora * (calado_max - calado_min)
        calado = np.clip(calado_base + np.random.normal(0, 0.5), calado_min, calado_max)
        calado = round(calado, 1)

        manga_min, manga_max = params['manga']
        manga_base = manga_min + factor_eslora * (manga_max - manga_min)
        manga = np.clip(manga_base + np.random.normal(0, 1.5), manga_min, manga_max)
        manga = round(manga, 1)

        gt_min, gt_max = params['gt']
        gt = int(gt_min + factor_eslora * (gt_max - gt_min) + np.random.normal(0, (gt_max-gt_min)*0.08))
        gt = max(gt_min, min(gt_max, gt))

        buques.append({
            'id_buque': i + 1,
            'nombre_buque': nombres_usados[i],
            'tipo_buque': tipo,
            'eslora_m': eslora,
            'calado_m': calado,
            'manga_m': manga,
            'bandera': random.choice(BANDERAS),
            'gt': gt
        })

    return pd.DataFrame(buques)

# ============================================================================
# LOGICA DE COMPATIBILIDAD BUQUE-MUELLE
# ============================================================================
COMPATIBILIDAD_CARGA_MUELLE = {
    'granel solido':  [1, 3, 4],   # Muelle Norte, Este, Oeste
    'granel liquido': [4],          # Muelle Oeste (bombeo)
    'carga general':  [1, 2, 3, 5], # Norte, Sur, Este, Ro-Ro
    'contenedores':   [2],          # Muelle Sur
    'carga rodada':   [5],          # Muelle Ro-Ro
}

# Tipo buque -> tipos de carga posibles (con pesos)
CARGA_POR_TIPO_BUQUE = {
    'granelero':         [('granel solido', 1.0)],
    'carga general':     [('carga general', 0.85), ('granel solido', 0.15)],
    'tanque':            [('granel liquido', 1.0)],
    'ro-ro':             [('carga rodada', 1.0)],
    'portacontenedores': [('contenedores', 1.0)],
}

# Tipo buque -> operacion (carga, descarga, ambas)
OPERACION_POR_TIPO = {
    'granelero':         [('descarga', 0.55), ('carga', 0.30), ('carga y descarga', 0.15)],
    'carga general':     [('descarga', 0.40), ('carga', 0.30), ('carga y descarga', 0.30)],
    'tanque':            [('descarga', 0.60), ('carga', 0.30), ('carga y descarga', 0.10)],
    'ro-ro':             [('descarga', 0.35), ('carga', 0.25), ('carga y descarga', 0.40)],
    'portacontenedores': [('descarga', 0.30), ('carga', 0.20), ('carga y descarga', 0.50)],
}

# Volumen de carga por tipo de buque (min, max, media, std) en toneladas
VOLUMEN_CARGA = {
    'granelero':         (3000, 35000, 15000, 7000),
    'carga general':     (500, 8000, 3000, 1800),
    'tanque':            (2000, 25000, 10000, 5500),
    'ro-ro':             (200, 3000, 1200, 600),
    'portacontenedores': (500, 6000, 2500, 1400),
}

# ============================================================================
# GENERACION DE ESCALAS
# ============================================================================

def generar_fechas_llegada(n_escalas, fecha_inicio, fecha_fin):
    """
    Genera ETAs distribuidos a lo largo del periodo, con:
    - Mayor concentracion L-V que S-D
    - Mayor concentracion diurna (06-18h)
    - Variabilidad interdiaria
    """
    n_dias = (fecha_fin - fecha_inicio).days + 1
    fechas = []

    for dia_offset in range(n_dias):
        fecha_dia = fecha_inicio + timedelta(days=dia_offset)
        dia_semana = fecha_dia.weekday()  # 0=lunes, 6=domingo

        # Tasa base de escalas por dia
        if dia_semana < 5:  # L-V
            tasa_base = np.random.poisson(2.2)
        else:  # S-D
            tasa_base = np.random.poisson(1.0)

        # Variabilidad adicional: algunos dias mas activos
        tasa_base = max(0, tasa_base + np.random.choice([-1, 0, 0, 0, 1], p=[0.1, 0.3, 0.3, 0.2, 0.1]))

        for _ in range(tasa_base):
            # Hora de llegada: 70% diurna, 30% nocturna
            if np.random.random() < 0.70:
                hora = np.random.normal(12, 3.5)
                hora = np.clip(hora, 6, 18)
            else:
                hora = np.random.choice([
                    np.random.uniform(0, 6),
                    np.random.uniform(18, 23.9)
                ])

            minuto = np.random.randint(0, 60)
            eta = fecha_dia + timedelta(hours=int(hora), minutes=minuto)
            fechas.append(eta)

    # Ajustar al numero deseado
    if len(fechas) > n_escalas:
        fechas = sorted(random.sample(fechas, n_escalas))
    elif len(fechas) < n_escalas:
        # Añadir mas fechas aleatorias
        for _ in range(n_escalas - len(fechas)):
            dia_random = fecha_inicio + timedelta(days=np.random.randint(0, n_dias))
            hora = np.random.uniform(0, 24)
            eta = dia_random + timedelta(hours=hora)
            fechas.append(eta)
        fechas = sorted(fechas)

    return fechas


def calcular_desviacion_eta():
    """
    Genera desviacion sobre ETA:
    25% anticipados (-3 a 0 h)
    35% desviacion minima (0 a +2 h)
    25% retraso moderado (+2 a +6 h)
    15% retraso significativo (+6 a +18 h)
    """
    r = np.random.random()
    if r < 0.25:
        return np.random.uniform(-3, 0)
    elif r < 0.60:
        return np.random.uniform(0, 2)
    elif r < 0.85:
        return np.random.uniform(2, 6)
    else:
        return np.random.uniform(6, 18)


def seleccionar_muelle(tipo_carga, eslora, calado, muelles_df, ocupacion_muelles, hora):
    """
    Selecciona muelle compatible y disponible.
    Retorna id_muelle o None si no hay muelle disponible.
    """
    muelles_compatibles = COMPATIBILIDAD_CARGA_MUELLE.get(tipo_carga, [])

    candidatos = []
    for m_id in muelles_compatibles:
        muelle = muelles_df[muelles_df['id_muelle'] == m_id].iloc[0]
        # Verificar restricciones fisicas
        if eslora > muelle['longitud_m']:
            continue
        if calado > muelle['calado_max_m']:
            continue
        # Verificar disponibilidad (no ocupado)
        if m_id not in ocupacion_muelles or ocupacion_muelles[m_id] <= hora:
            candidatos.append(m_id)

    if not candidatos:
        # Intentar asignacion suboptima: muelle de otro tipo pero fisicamente compatible
        for m_id in range(1, 6):
            if m_id in muelles_compatibles:
                continue
            muelle = muelles_df[muelles_df['id_muelle'] == m_id].iloc[0]
            if eslora <= muelle['longitud_m'] and calado <= muelle['calado_max_m']:
                if m_id not in ocupacion_muelles or ocupacion_muelles[m_id] <= hora:
                    # Solo si el tipo de carga no es totalmente incompatible
                    if tipo_carga not in ['granel liquido', 'carga rodada']:
                        candidatos.append(m_id)
                        break

    if candidatos:
        # Preferir el primero compatible (mejor asignacion)
        return candidatos[0], (candidatos[0] not in COMPATIBILIDAD_CARGA_MUELLE.get(tipo_carga, []))

    return None, False


def calcular_tiempo_servicio(tipo_buque, volumen, tipo_carga, es_suboptimo, n_gruas):
    """
    Calcula tiempo de servicio basado en tipo, volumen y recursos.
    Retorna horas.
    """
    # Rendimiento base por tipo (toneladas/hora total de la operacion)
    # Valores ajustados para terminal polivalente de tamaño medio
    rendimientos = {
        'granelero':         (500, 1000),
        'carga general':     (150, 400),
        'tanque':            (500, 1000),
        'ro-ro':             (100, 300),
        'portacontenedores': (200, 500),
    }

    rend_min, rend_max = rendimientos[tipo_buque]
    rendimiento = np.random.uniform(rend_min, rend_max)

    # Ajustar por numero de gruas (efecto no lineal)
    if n_gruas >= 2:
        rendimiento *= 1.6  # No se duplica por ineficiencias

    # Tiempo base
    tiempo_base = volumen / rendimiento if rendimiento > 0 else 24

    # Tiempo minimo por maniobras, preparacion, etc.
    tiempo_min = {
        'granelero': 6, 'carga general': 4, 'tanque': 5,
        'ro-ro': 2, 'portacontenedores': 3
    }
    tiempo = max(tiempo_base, tiempo_min[tipo_buque])

    # Añadir tiempo de maniobra de atraque/desatraque (1-2h)
    tiempo += np.random.uniform(1, 2.5)

    # Penalizacion por asignacion suboptima (10-25% mas)
    if es_suboptimo:
        tiempo *= np.random.uniform(1.10, 1.25)

    # Ruido aleatorio +-15%
    tiempo *= np.random.uniform(0.85, 1.15)

    return round(tiempo, 2)


def generar_escalas(buques_df, muelles_df, n_escalas=180):
    """Genera la tabla principal de escalas."""

    # Generar ETAs
    etas = generar_fechas_llegada(n_escalas, FECHA_INICIO, FECHA_FIN)

    # ---- EPISODIOS ESPECIALES ----
    # Episodios meteorologicos: 3 periodos de 1-3 dias con mal tiempo
    episodios_meteo = []
    dias_meteo_inicio = sorted(random.sample(range(10, NUM_DIAS - 10), 3))
    for d in dias_meteo_inicio:
        duracion = np.random.randint(1, 4)
        inicio = FECHA_INICIO + timedelta(days=d)
        fin = inicio + timedelta(days=duracion)
        episodios_meteo.append((inicio, fin))

    # Picos de congestion: 5 periodos de 1-2 dias con alta llegada
    picos_congestion = sorted(random.sample(range(5, NUM_DIAS - 5), 5))

    # Averias de grua: 4 eventos
    averias_programadas = []
    dias_averia = sorted(random.sample(range(0, NUM_DIAS), 4))
    for d in dias_averia:
        inicio_averia = FECHA_INICIO + timedelta(days=d, hours=np.random.randint(6, 18))
        duracion_averia = np.random.uniform(4, 48)
        fin_averia = inicio_averia + timedelta(hours=duracion_averia)
        recurso_afectado = np.random.choice([1, 2, 3, 4, 5])  # Gruas
        averias_programadas.append((inicio_averia, fin_averia, recurso_afectado))

    # ---- GENERACION DE ESCALAS ----
    escalas = []
    incidencias_lista = []
    asignaciones_lista = []

    # Control de ocupacion de muelles: {id_muelle: datetime_liberacion}
    ocupacion_muelles = {}

    id_escala = 0
    id_incidencia = 0
    id_asignacion = 0

    for idx, eta in enumerate(etas):
        id_escala += 1

        # Seleccionar buque (pueden repetir, un buque hace multiples escalas)
        buque = buques_df.sample(1).iloc[0]
        tipo_buque = buque['tipo_buque']
        eslora = buque['eslora_m']
        calado = buque['calado_m']

        # Tipo de carga
        opciones_carga = CARGA_POR_TIPO_BUQUE[tipo_buque]
        tipo_carga = np.random.choice(
            [c[0] for c in opciones_carga],
            p=[c[1] for c in opciones_carga]
        )

        # Operacion
        opciones_op = OPERACION_POR_TIPO[tipo_buque]
        operacion = np.random.choice(
            [o[0] for o in opciones_op],
            p=[o[1] for o in opciones_op]
        )

        # Volumen de carga (correlacionado con eslora)
        vol_params = VOLUMEN_CARGA[tipo_buque]
        eslora_params = PARAMS_BUQUE[tipo_buque]['eslora']
        factor_eslora = (eslora - eslora_params[0]) / (eslora_params[1] - eslora_params[0])
        vol_base = vol_params[0] + factor_eslora * (vol_params[1] - vol_params[0])
        volumen = np.clip(
            vol_base + np.random.normal(0, vol_params[3] * 0.5),
            vol_params[0], vol_params[1]
        )
        volumen = round(volumen, 1)
        if operacion == 'carga y descarga':
            volumen = round(volumen * np.random.uniform(1.1, 1.6), 1)
            volumen = min(volumen, vol_params[1] * 1.3)

        # Prioridad
        r_prio = np.random.random()
        if r_prio < 0.15:
            prioridad = 'alta'
        elif r_prio < 0.70:
            prioridad = 'media'
        else:
            prioridad = 'baja'

        # Desviacion sobre ETA
        desviacion = calcular_desviacion_eta()
        ata = eta + timedelta(hours=desviacion)

        # ---- Verificar episodios meteorologicos ----
        en_meteo = False
        for (m_ini, m_fin) in episodios_meteo:
            if m_ini <= ata <= m_fin:
                en_meteo = True
                break

        # ---- Asignacion de muelle ----
        muelle_id, es_suboptimo = seleccionar_muelle(
            tipo_carga, eslora, calado, muelles_df, ocupacion_muelles, ata
        )

        # Calcular tiempo de espera
        causa_espera = 'sin espera significativa'
        tiempo_espera = 0

        if muelle_id is None:
            # No hay muelle disponible: esperar
            # Buscar el muelle compatible que se libera antes
            muelles_compatibles = COMPATIBILIDAD_CARGA_MUELLE.get(tipo_carga, [])
            mejor_hora = None
            mejor_muelle = None
            for m_id in muelles_compatibles:
                muelle_info = muelles_df[muelles_df['id_muelle'] == m_id].iloc[0]
                if eslora > muelle_info['longitud_m'] or calado > muelle_info['calado_max_m']:
                    continue
                if m_id in ocupacion_muelles:
                    if mejor_hora is None or ocupacion_muelles[m_id] < mejor_hora:
                        mejor_hora = ocupacion_muelles[m_id]
                        mejor_muelle = m_id

            if mejor_muelle is not None:
                muelle_id = mejor_muelle
                espera_muelle = (mejor_hora - ata).total_seconds() / 3600
                tiempo_espera = max(0, espera_muelle)
                causa_espera = 'muelle ocupado'
                es_suboptimo = False
            else:
                # Forzar asignacion al primer muelle fisicamente posible
                for m_id in range(1, 6):
                    muelle_info = muelles_df[muelles_df['id_muelle'] == m_id].iloc[0]
                    if eslora <= muelle_info['longitud_m'] and calado <= muelle_info['calado_max_m']:
                        muelle_id = m_id
                        if m_id in ocupacion_muelles:
                            espera_muelle = (ocupacion_muelles[m_id] - ata).total_seconds() / 3600
                            tiempo_espera = max(0, espera_muelle)
                        causa_espera = 'congestion general de la terminal'
                        es_suboptimo = True
                        break
                if muelle_id is None:
                    muelle_id = 1  # Fallback extremo
                    tiempo_espera = np.random.uniform(6, 18)
                    causa_espera = 'congestion general de la terminal'
                    es_suboptimo = True

        # Esperas adicionales por practicaje, meteorologia, etc.
        if en_meteo:
            tiempo_espera += np.random.uniform(2, 12)
            causa_espera = 'condiciones meteorologicas adversas'

        # Espera adicional por prioridad baja en periodos de alta ocupacion
        muelles_ocupados = sum(1 for m, t in ocupacion_muelles.items() if t > ata)
        if muelles_ocupados >= 3 and prioridad == 'baja':
            extra = np.random.uniform(1, 6)
            tiempo_espera += extra
            if causa_espera == 'sin espera significativa':
                causa_espera = 'congestion general de la terminal'

        # Espera por practicaje (ocasional, ~10% de escalas)
        if np.random.random() < 0.10 and causa_espera == 'sin espera significativa':
            tiempo_espera += np.random.uniform(0.5, 3)
            causa_espera = 'espera de practicaje'

        # Espera por documentacion (ocasional, ~5%)
        if np.random.random() < 0.05 and causa_espera == 'sin espera significativa':
            tiempo_espera += np.random.uniform(0.5, 2)
            causa_espera = 'espera documental / despacho'

        # Espera minima por maniobra previa
        if tiempo_espera < 0.25 and causa_espera == 'sin espera significativa':
            tiempo_espera = round(np.random.uniform(0.1, 0.5), 2)

        # Tope maximo realista de espera: 36 horas (mas alla se desviaria a otro puerto)
        # Las esperas muy largas se comprimen con un tope suave
        if tiempo_espera > 36:
            tiempo_espera = 36 + np.random.uniform(0, 6)  # max ~42h en casos extremos
        elif tiempo_espera > 24:
            # Comprimir ligeramente las esperas entre 24 y 36h
            exceso = tiempo_espera - 24
            tiempo_espera = 24 + exceso * np.random.uniform(0.3, 0.6)

        tiempo_espera = round(max(0, tiempo_espera), 2)

        # Hora de inicio de operacion
        hora_inicio_op = ata + timedelta(hours=tiempo_espera)

        # ---- Asignacion de recursos ----
        n_gruas = 0
        recursos_escala = []

        if tipo_buque == 'granelero':
            # 1-2 gruas (portico si muelle 1 o 2, movil si muelle 3)
            if muelle_id in [1]:
                recursos_escala.append(1)  # Grua portico MN-01
                n_gruas = 1
                if volumen > 20000 and np.random.random() < 0.6:
                    recursos_escala.append(np.random.choice([3, 4, 5]))
                    n_gruas = 2
            elif muelle_id in [3]:
                recursos_escala.append(np.random.choice([3, 4, 5]))
                n_gruas = 1
                if volumen > 18000 and np.random.random() < 0.5:
                    gruas_disponibles = [g for g in [3, 4, 5] if g not in recursos_escala]
                    if gruas_disponibles:
                        recursos_escala.append(np.random.choice(gruas_disponibles))
                        n_gruas = 2
            else:
                recursos_escala.append(np.random.choice([3, 4, 5]))
                n_gruas = 1
            # Palas y cintas
            recursos_escala.extend(random.sample([6, 7, 8], np.random.randint(1, 3)))
            if volumen > 10000:
                recursos_escala.append(np.random.choice([9, 10]))
            # Tolva
            if np.random.random() < 0.5:
                recursos_escala.append(np.random.choice([11, 12]))
            # Equipo estiba
            recursos_escala.extend(random.sample([24, 25, 26, 27], np.random.randint(1, 3)))

        elif tipo_buque == 'carga general':
            if muelle_id in [1, 2]:
                recursos_escala.append(1 if muelle_id == 1 else 2)
                n_gruas = 1
            else:
                recursos_escala.append(np.random.choice([3, 4, 5]))
                n_gruas = 1
            # Carretillas
            recursos_escala.extend(random.sample([13, 14, 15], np.random.randint(1, 3)))
            # Tractoras
            if np.random.random() < 0.6:
                recursos_escala.append(np.random.choice([18, 19, 20, 21]))
            # Equipo estiba
            recursos_escala.extend(random.sample([24, 25, 26, 27], np.random.randint(1, 2)))

        elif tipo_buque == 'tanque':
            # Equipo de bombeo
            recursos_escala.append(np.random.choice([22, 23]))
            if volumen > 15000:
                bombas_disp = [b for b in [22, 23] if b not in recursos_escala]
                if bombas_disp:
                    recursos_escala.append(bombas_disp[0])
            n_gruas = 0
            # Equipo supervision
            recursos_escala.append(np.random.choice([24, 25, 26, 27]))

        elif tipo_buque == 'ro-ro':
            # Tractoras
            recursos_escala.extend(random.sample([18, 19, 20, 21], np.random.randint(1, 3)))
            # Equipo estiba
            recursos_escala.append(np.random.choice([24, 25, 26, 27]))
            n_gruas = 0

        elif tipo_buque == 'portacontenedores':
            if muelle_id == 2:
                recursos_escala.append(2)  # Grua portico MS-01
                n_gruas = 1
            else:
                recursos_escala.append(np.random.choice([3, 4, 5]))
                n_gruas = 1
            # Reach stackers y tractoras
            recursos_escala.extend(random.sample([16, 17], np.random.randint(1, 2)))
            recursos_escala.extend(random.sample([18, 19, 20, 21], np.random.randint(1, 3)))
            # Equipo estiba
            recursos_escala.extend(random.sample([24, 25, 26, 27], np.random.randint(1, 2)))

        # Eliminar duplicados
        recursos_escala = list(set(recursos_escala))

        # ---- Tiempo de servicio ----
        tiempo_servicio = calcular_tiempo_servicio(
            tipo_buque, volumen, tipo_carga, es_suboptimo, n_gruas
        )

        # ---- Efecto turno nocturno: +5-10% si operacion en horario nocturno ----
        hora_op = hora_inicio_op.hour
        if hora_op >= 22 or hora_op < 6:
            tiempo_servicio *= np.random.uniform(1.05, 1.12)
            tiempo_servicio = round(tiempo_servicio, 2)

        # Hora de fin de operacion
        hora_fin_op = hora_inicio_op + timedelta(hours=tiempo_servicio)

        # Tiempo total
        tiempo_total = round(tiempo_espera + tiempo_servicio, 2)

        # Actualizar ocupacion del muelle
        ocupacion_muelles[muelle_id] = hora_fin_op

        # ---- INCIDENCIAS ----
        # Probabilidad base ~22%, mayor en episodios meteo
        prob_incidencia = 0.22
        if en_meteo:
            prob_incidencia = 0.65

        # Verificar si coincide con averia programada
        averia_activa = None
        for (av_ini, av_fin, av_rec) in averias_programadas:
            if av_ini <= hora_inicio_op <= av_fin or av_ini <= hora_fin_op <= av_fin:
                averia_activa = (av_ini, av_fin, av_rec)
                break

        tiene_incidencia = np.random.random() < prob_incidencia or averia_activa is not None

        if tiene_incidencia:
            id_incidencia += 1

            if averia_activa is not None:
                tipo_inc = 'averia de equipo'
                dur_inc = min(
                    (averia_activa[1] - max(averia_activa[0], hora_inicio_op)).total_seconds() / 3600,
                    tiempo_servicio * 0.4
                )
                dur_inc = round(max(1, dur_inc), 2)
                rec_afectado = averia_activa[2]
                desc_inc = f'Averia en {averia_activa[2]} durante operacion'
                # Alargar tiempo de servicio
                penalizacion = dur_inc * np.random.uniform(0.3, 0.7)
                tiempo_servicio = round(tiempo_servicio + penalizacion, 2)
                hora_fin_op = hora_inicio_op + timedelta(hours=tiempo_servicio)
                tiempo_total = round(tiempo_espera + tiempo_servicio, 2)
                ocupacion_muelles[muelle_id] = hora_fin_op
            elif en_meteo:
                tipo_inc = 'condiciones meteorologicas adversas'
                dur_inc = round(np.random.uniform(1, 8), 2)
                rec_afectado = None
                desc_inc = 'Paralizacion parcial o total por viento/lluvia'
                penalizacion = dur_inc * np.random.uniform(0.5, 1.0)
                tiempo_servicio = round(tiempo_servicio + penalizacion, 2)
                hora_fin_op = hora_inicio_op + timedelta(hours=tiempo_servicio)
                tiempo_total = round(tiempo_espera + tiempo_servicio, 2)
                ocupacion_muelles[muelle_id] = hora_fin_op
            else:
                # Incidencia aleatoria
                tipos_inc_opciones = [
                    ('averia de equipo', 0.20),
                    ('indisponibilidad de recurso por turno', 0.22),
                    ('congestion de muelle', 0.15),
                    ('problema documental o administrativo', 0.15),
                    ('falta de personal', 0.08),
                    ('fallo de coordinacion', 0.12),
                    ('otro', 0.08),
                ]
                tipo_inc = np.random.choice(
                    [t[0] for t in tipos_inc_opciones],
                    p=[t[1] for t in tipos_inc_opciones]
                )

                if tipo_inc == 'averia de equipo':
                    dur_inc = round(np.random.uniform(0.5, 6), 2)
                    rec_afectado = np.random.choice(recursos_escala) if recursos_escala else None
                    desc_inc = 'Averia menor en equipo de operacion'
                elif tipo_inc == 'indisponibilidad de recurso por turno':
                    dur_inc = round(np.random.uniform(0.5, 3), 2)
                    rec_afectado = np.random.choice(recursos_escala) if recursos_escala else None
                    desc_inc = 'Recurso no disponible al inicio del turno siguiente'
                elif tipo_inc == 'congestion de muelle':
                    dur_inc = round(np.random.uniform(1, 4), 2)
                    rec_afectado = None
                    desc_inc = 'Retraso por congestion en zona de muelle'
                elif tipo_inc == 'problema documental o administrativo':
                    dur_inc = round(np.random.uniform(0.5, 2.5), 2)
                    rec_afectado = None
                    desc_inc = 'Demora por tramites documentales o despacho'
                elif tipo_inc == 'falta de personal':
                    dur_inc = round(np.random.uniform(1, 4), 2)
                    rec_afectado = None
                    desc_inc = 'Retraso por falta de personal de estiba en turno'
                elif tipo_inc == 'fallo de coordinacion':
                    dur_inc = round(np.random.uniform(0.5, 3), 2)
                    rec_afectado = None
                    desc_inc = 'Descoordinacion entre servicios o agentes'
                else:
                    dur_inc = round(np.random.uniform(0.5, 2), 2)
                    rec_afectado = None
                    desc_inc = 'Incidencia menor no clasificada'

                # Impacto sobre tiempo de servicio
                penalizacion = dur_inc * np.random.uniform(0.3, 0.8)
                tiempo_servicio = round(tiempo_servicio + penalizacion, 2)
                hora_fin_op = hora_inicio_op + timedelta(hours=tiempo_servicio)
                tiempo_total = round(tiempo_espera + tiempo_servicio, 2)
                ocupacion_muelles[muelle_id] = hora_fin_op

            # Impacto
            if dur_inc < 1:
                impacto = 'bajo'
            elif dur_inc < 4:
                impacto = 'moderado'
            else:
                impacto = 'alto'

            hora_inicio_inc = hora_inicio_op + timedelta(
                hours=np.random.uniform(0, max(0.1, tiempo_servicio * 0.5))
            )
            hora_fin_inc = hora_inicio_inc + timedelta(hours=dur_inc)

            incidencias_lista.append({
                'id_incidencia': id_incidencia,
                'id_escala': id_escala,
                'tipo_incidencia': tipo_inc,
                'descripcion': desc_inc,
                'hora_inicio': hora_inicio_inc,
                'hora_fin': hora_fin_inc,
                'duracion_h': dur_inc,
                'impacto_estimado': impacto,
                'recurso_afectado': rec_afectado
            })

        # ---- Asignacion de recursos ----
        for rec_id in recursos_escala:
            id_asignacion += 1
            # El recurso se usa durante la operacion (con variabilidad)
            inicio_uso = hora_inicio_op + timedelta(
                hours=np.random.uniform(0, 0.5)
            )
            horas_uso = tiempo_servicio * np.random.uniform(0.6, 0.95)
            fin_uso = inicio_uso + timedelta(hours=horas_uso)

            obs_rec = ''
            if es_suboptimo and np.random.random() < 0.3:
                obs_rec = 'Recurso reasignado por indisponibilidad de muelle preferente'

            asignaciones_lista.append({
                'id_asignacion': id_asignacion,
                'id_escala': id_escala,
                'id_recurso': rec_id,
                'hora_inicio_uso': inicio_uso,
                'hora_fin_uso': fin_uso,
                'horas_uso': round(horas_uso, 2),
                'observaciones': obs_rec
            })

        # ---- Observaciones de la escala ----
        observaciones = ''
        if es_suboptimo:
            observaciones = 'Muelle asignado no es el preferente para este tipo de carga'
        elif en_meteo:
            observaciones = 'Escala afectada por episodio meteorologico adverso'
        elif tiempo_espera > 8:
            observaciones = 'Espera prolongada por alta ocupacion de terminal'
        elif np.random.random() < 0.04:
            observaciones = ''  # Campo vacio deliberado (dato incompleto)

        # Redondear desviacion
        desviacion_h = round(desviacion, 2)

        escalas.append({
            'id_escala': id_escala,
            'id_buque': buque['id_buque'],
            'id_muelle': muelle_id,
            'tipo_carga': tipo_carga,
            'volumen_carga_t': volumen,
            'operacion': operacion,
            'prioridad': prioridad,
            'eta': eta,
            'ata': ata,
            'hora_inicio_op': hora_inicio_op,
            'hora_fin_op': hora_fin_op,
            'tiempo_espera_h': tiempo_espera,
            'tiempo_servicio_h': round(tiempo_servicio, 2),
            'tiempo_total_h': round(tiempo_espera + tiempo_servicio, 2),
            'desviacion_eta_h': desviacion_h,
            'causa_espera': causa_espera,
            'observaciones': observaciones
        })

    df_escalas = pd.DataFrame(escalas)
    df_incidencias = pd.DataFrame(incidencias_lista)
    df_asignaciones = pd.DataFrame(asignaciones_lista)

    return df_escalas, df_incidencias, df_asignaciones


# ============================================================================
# GENERACION PRINCIPAL
# ============================================================================
def main():
    print("=" * 70)
    print("GENERADOR DE DATASET SIMULADO - TFG EFICIENCIA PORTUARIA")
    print("=" * 70)
    print(f"Semilla aleatoria: {SEED}")
    print(f"Periodo: {FECHA_INICIO.strftime('%Y-%m-%d')} a {FECHA_FIN.strftime('%Y-%m-%d')}")
    print()

    # Generar tablas maestras
    print("[1/4] Generando tabla de muelles...")
    muelles = generar_muelles()

    print("[2/4] Generando tabla de recursos...")
    recursos = generar_recursos()

    print("[3/4] Generando catalogo de buques...")
    buques = generar_buques(76)

    print("[4/4] Generando escalas, incidencias y asignaciones de recursos...")
    escalas, incidencias, asignaciones = generar_escalas(buques, muelles, n_escalas=180)

    # ---- ESTADISTICAS RESUMEN ----
    print()
    print("=" * 70)
    print("RESUMEN DEL DATASET GENERADO")
    print("=" * 70)
    print(f"Buques en catalogo:           {len(buques)}")
    print(f"Muelles:                      {len(muelles)}")
    print(f"Recursos:                     {len(recursos)}")
    print(f"Escalas generadas:            {len(escalas)}")
    print(f"Incidencias registradas:      {len(incidencias)}")
    print(f"Asignaciones de recursos:     {len(asignaciones)}")
    print()

    print("--- Distribucion por tipo de buque ---")
    buques_en_escalas = escalas.merge(buques[['id_buque', 'tipo_buque']], on='id_buque')
    print(buques_en_escalas['tipo_buque'].value_counts().to_string())
    print()

    print("--- Distribucion por muelle ---")
    print(escalas['id_muelle'].value_counts().sort_index().to_string())
    print()

    print("--- Tiempos medios ---")
    print(f"  Tiempo medio de espera:     {escalas['tiempo_espera_h'].mean():.2f} h")
    print(f"  Tiempo medio de servicio:   {escalas['tiempo_servicio_h'].mean():.2f} h")
    print(f"  Tiempo medio total:         {escalas['tiempo_total_h'].mean():.2f} h")
    print(f"  Mediana de espera:          {escalas['tiempo_espera_h'].median():.2f} h")
    print(f"  Max espera:                 {escalas['tiempo_espera_h'].max():.2f} h")
    print()

    print("--- Desviacion sobre ETA ---")
    print(f"  Media:                      {escalas['desviacion_eta_h'].mean():.2f} h")
    print(f"  % anticipados (< 0):        {(escalas['desviacion_eta_h'] < 0).mean()*100:.1f}%")
    print(f"  % retraso > 6h:             {(escalas['desviacion_eta_h'] > 6).mean()*100:.1f}%")
    print()

    print("--- Incidencias ---")
    if len(incidencias) > 0:
        print(f"  % escalas con incidencia:   {incidencias['id_escala'].nunique() / len(escalas) * 100:.1f}%")
        print(f"  Distribucion por tipo:")
        print(incidencias['tipo_incidencia'].value_counts().to_string())
        print()
        print(f"  Distribucion por impacto:")
        print(incidencias['impacto_estimado'].value_counts().to_string())
    print()

    print("--- Causas de espera ---")
    print(escalas['causa_espera'].value_counts().to_string())
    print()

    print("--- Prioridad ---")
    print(escalas['prioridad'].value_counts().to_string())
    print()

    # ---- GUARDAR ARCHIVOS ----
    ruta_base = '/Users/javierlopezgil/Desktop/TFG_Portuario/datos/'

    # Formatear fechas para CSV
    fecha_cols_escalas = ['eta', 'ata', 'hora_inicio_op', 'hora_fin_op']
    for col in fecha_cols_escalas:
        escalas[col] = pd.to_datetime(escalas[col]).dt.strftime('%Y-%m-%d %H:%M')

    if len(incidencias) > 0:
        for col in ['hora_inicio', 'hora_fin']:
            incidencias[col] = pd.to_datetime(incidencias[col]).dt.strftime('%Y-%m-%d %H:%M')

    for col in ['hora_inicio_uso', 'hora_fin_uso']:
        asignaciones[col] = pd.to_datetime(asignaciones[col]).dt.strftime('%Y-%m-%d %H:%M')

    muelles.to_csv(ruta_base + '01_muelles.csv', index=False, encoding='utf-8-sig')
    recursos.to_csv(ruta_base + '02_recursos.csv', index=False, encoding='utf-8-sig')
    buques.to_csv(ruta_base + '03_buques.csv', index=False, encoding='utf-8-sig')
    escalas.to_csv(ruta_base + '04_escalas.csv', index=False, encoding='utf-8-sig')
    incidencias.to_csv(ruta_base + '05_incidencias.csv', index=False, encoding='utf-8-sig')
    asignaciones.to_csv(ruta_base + '06_asignacion_recursos.csv', index=False, encoding='utf-8-sig')

    print(f"Archivos guardados en: {ruta_base}")
    print("  01_muelles.csv")
    print("  02_recursos.csv")
    print("  03_buques.csv")
    print("  04_escalas.csv")
    print("  05_incidencias.csv")
    print("  06_asignacion_recursos.csv")
    print()
    print("=" * 70)
    print("GENERACION COMPLETADA")
    print("=" * 70)


if __name__ == '__main__':
    main()
