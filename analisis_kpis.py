"""
=============================================================================
ANALISIS DE KPIs Y DIAGNOSTICO OPERATIVO - TFG EFICIENCIA PORTUARIA
=============================================================================
Calcula todos los KPIs definidos en la metodologia sobre el escenario base
y genera tablas, graficos y diagnostico cuantitativo.
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
sns.set_palette("muted")

RUTA = '/Users/javierlopezgil/Desktop/TFG_Portuario/datos/'
RUTA_FIG = '/Users/javierlopezgil/Desktop/TFG_Portuario/figuras/'

import os
os.makedirs(RUTA_FIG, exist_ok=True)

# ============================================================================
# CARGA DE DATOS
# ============================================================================
muelles = pd.read_csv(RUTA + '01_muelles.csv')
recursos = pd.read_csv(RUTA + '02_recursos.csv')
buques = pd.read_csv(RUTA + '03_buques.csv')
escalas = pd.read_csv(RUTA + '04_escalas.csv')
incidencias = pd.read_csv(RUTA + '05_incidencias.csv')
asignaciones = pd.read_csv(RUTA + '06_asignacion_recursos.csv')

# Parsear fechas
for col in ['eta', 'ata', 'hora_inicio_op', 'hora_fin_op']:
    escalas[col] = pd.to_datetime(escalas[col])
for col in ['hora_inicio', 'hora_fin']:
    incidencias[col] = pd.to_datetime(incidencias[col])
for col in ['hora_inicio_uso', 'hora_fin_uso']:
    asignaciones[col] = pd.to_datetime(asignaciones[col])

# Merge tipo_buque
esc = escalas.merge(buques[['id_buque', 'tipo_buque', 'eslora_m']], on='id_buque')

# Nombres de muelles
nombres_muelles = dict(zip(muelles['id_muelle'], muelles['nombre_muelle']))
esc['nombre_muelle'] = esc['id_muelle'].map(nombres_muelles)

HORAS_PERIODO = 91 * 24  # 2184 horas

print("=" * 80)
print("CALCULO DE KPIs - ESCENARIO BASE")
print("=" * 80)

# ============================================================================
# 1. KPIs DE TIEMPO
# ============================================================================
print("\n" + "=" * 80)
print("1. KPIs DE TIEMPO")
print("=" * 80)

# 1.1 Tiempo medio de espera (AWT)
awt = esc['tiempo_espera_h'].mean()
awt_mediana = esc['tiempo_espera_h'].median()
awt_std = esc['tiempo_espera_h'].std()
awt_max = esc['tiempo_espera_h'].max()
print(f"\n  AWT (media):    {awt:.2f} h")
print(f"  AWT (mediana):  {awt_mediana:.2f} h")
print(f"  AWT (desv.tip): {awt_std:.2f} h")
print(f"  AWT (max):      {awt_max:.2f} h")

# 1.2 Tiempo medio de servicio (AST)
ast_val = esc['tiempo_servicio_h'].mean()
ast_mediana = esc['tiempo_servicio_h'].median()
print(f"\n  AST (media):    {ast_val:.2f} h")
print(f"  AST (mediana):  {ast_mediana:.2f} h")

# 1.3 Tiempo medio de estancia (ATT)
att = esc['tiempo_total_h'].mean()
att_mediana = esc['tiempo_total_h'].median()
print(f"\n  ATT (media):    {att:.2f} h")
print(f"  ATT (mediana):  {att_mediana:.2f} h")

# 1.4 Ratio de espera (WTR)
wtr_global = awt / ast_val
print(f"\n  WTR global:     {wtr_global:.3f}")
print(f"  Umbral ref.:    0.300 {'⚠ SUPERADO' if wtr_global > 0.3 else '✓ Dentro del rango'}")

# 1.5 Desviacion media sobre ETA
desv_media = esc['desviacion_eta_h'].mean()
desv_abs_media = esc['desviacion_eta_h'].abs().mean()
print(f"\n  Desviacion media ETA:     {desv_media:+.2f} h")
print(f"  Desviacion absoluta media: {desv_abs_media:.2f} h")

# 1.6 % escalas con espera > 6h
pct_espera_6h = (esc['tiempo_espera_h'] > 6).mean() * 100
pct_espera_12h = (esc['tiempo_espera_h'] > 12).mean() * 100
pct_espera_24h = (esc['tiempo_espera_h'] > 24).mean() * 100
print(f"\n  % escalas espera > 6h:  {pct_espera_6h:.1f}%")
print(f"  % escalas espera > 12h: {pct_espera_12h:.1f}%")
print(f"  % escalas espera > 24h: {pct_espera_24h:.1f}%")

# Desglose por tipo de buque
print("\n  --- Tiempos por tipo de buque ---")
tabla_tipos = esc.groupby('tipo_buque').agg(
    n=('id_escala', 'count'),
    espera_media=('tiempo_espera_h', 'mean'),
    espera_mediana=('tiempo_espera_h', 'median'),
    servicio_media=('tiempo_servicio_h', 'mean'),
    total_media=('tiempo_total_h', 'mean'),
    wtr=('tiempo_espera_h', lambda x: x.mean() / esc.loc[x.index, 'tiempo_servicio_h'].mean())
).round(2)
print(tabla_tipos.to_string())

# Desglose por prioridad
print("\n  --- Tiempos por prioridad ---")
tabla_prio = esc.groupby('prioridad').agg(
    n=('id_escala', 'count'),
    espera_media=('tiempo_espera_h', 'mean'),
    espera_mediana=('tiempo_espera_h', 'median'),
    pct_espera_6h=('tiempo_espera_h', lambda x: (x > 6).mean() * 100)
).round(2)
print(tabla_prio.to_string())

# ============================================================================
# 2. KPIs DE INFRAESTRUCTURA
# ============================================================================
print("\n" + "=" * 80)
print("2. KPIs DE INFRAESTRUCTURA (MUELLES)")
print("=" * 80)

# 2.1 BOR por muelle
print("\n  --- Tasa de Ocupacion de Muelles (BOR) ---")
bor_muelles = {}
for m_id in range(1, 6):
    esc_m = esc[esc['id_muelle'] == m_id]
    horas_ocupadas = esc_m['tiempo_servicio_h'].sum()
    bor = horas_ocupadas / HORAS_PERIODO * 100
    bor_muelles[m_id] = bor
    nombre = nombres_muelles[m_id]
    estado = ''
    if bor > 70:
        estado = '⚠ CONGESTION'
    elif bor > 55:
        estado = '⚠ Alto'
    elif bor < 20:
        estado = '↓ Infrautilizado'
    print(f"  {nombre:20s}: {esc_m.shape[0]:3d} escalas | {horas_ocupadas:7.1f}h ocupado | BOR = {bor:5.1f}% {estado}")

bor_global = sum(esc['tiempo_servicio_h']) / (5 * HORAS_PERIODO) * 100
print(f"\n  BOR global (5 muelles): {bor_global:.1f}%")

# 2.2 Tiempo medio entre escalas por muelle
print("\n  --- Tiempo medio entre escalas (gap) por muelle ---")
for m_id in range(1, 6):
    esc_m = esc[esc['id_muelle'] == m_id].sort_values('hora_inicio_op')
    if len(esc_m) < 2:
        continue
    gaps = []
    for i in range(len(esc_m) - 1):
        gap = (esc_m.iloc[i+1]['hora_inicio_op'] - esc_m.iloc[i]['hora_fin_op']).total_seconds() / 3600
        if gap >= 0:
            gaps.append(gap)
    if gaps:
        nombre = nombres_muelles[m_id]
        print(f"  {nombre:20s}: gap medio = {np.mean(gaps):6.1f}h | gap mediana = {np.median(gaps):6.1f}h | min = {np.min(gaps):.1f}h | max = {np.max(gaps):.1f}h")

# 2.3 Indice de compatibilidad buque-muelle
COMPAT = {
    'granel solido':  [1, 3, 4],
    'granel liquido': [4],
    'carga general':  [1, 2, 3, 5],
    'contenedores':   [2],
    'carga rodada':   [5],
}
asignaciones_optimas = 0
for _, row in esc.iterrows():
    muelles_ideales = COMPAT.get(row['tipo_carga'], [])
    if row['id_muelle'] in muelles_ideales:
        asignaciones_optimas += 1
idx_compat = asignaciones_optimas / len(esc) * 100
print(f"\n  Indice de compatibilidad buque-muelle: {idx_compat:.1f}%")
print(f"  Asignaciones suboptimas: {len(esc) - asignaciones_optimas} ({100 - idx_compat:.1f}%)")

# ============================================================================
# 3. KPIs DE RECURSOS
# ============================================================================
print("\n" + "=" * 80)
print("3. KPIs DE RECURSOS")
print("=" * 80)

# 3.1 Recursos medios por escala
recursos_por_escala = asignaciones.groupby('id_escala')['id_recurso'].count()
print(f"\n  Recursos medios por escala:  {recursos_por_escala.mean():.1f}")
print(f"  Rango:                       {recursos_por_escala.min()} - {recursos_por_escala.max()}")

# Recursos por tipo de buque
esc_rec = esc[['id_escala', 'tipo_buque']].merge(
    recursos_por_escala.rename('n_recursos'), on='id_escala'
)
print("\n  --- Recursos medios por tipo de buque ---")
print(esc_rec.groupby('tipo_buque')['n_recursos'].agg(['mean', 'min', 'max']).round(1).to_string())

# 3.2 Tasa de utilizacion de gruas
gruas_ids = recursos[recursos['tipo_recurso'].isin(['grua portico', 'grua movil'])]['id_recurso'].tolist()
asig_gruas = asignaciones[asignaciones['id_recurso'].isin(gruas_ids)]
print(f"\n  --- Utilizacion de gruas ---")
for g_id in gruas_ids:
    asig_g = asig_gruas[asig_gruas['id_recurso'] == g_id]
    horas_uso = asig_g['horas_uso'].sum()
    tasa = horas_uso / HORAS_PERIODO * 100
    nombre = recursos[recursos['id_recurso'] == g_id]['nombre_recurso'].iloc[0]
    print(f"  {nombre:30s}: {horas_uso:7.1f}h uso | Tasa = {tasa:5.1f}%")

horas_gruas_total = asig_gruas['horas_uso'].sum()
tasa_gruas_global = horas_gruas_total / (len(gruas_ids) * HORAS_PERIODO) * 100
print(f"\n  Tasa utilizacion gruas (global): {tasa_gruas_global:.1f}%")

# 3.3 % escalas con tension de recursos (reasignacion o nota)
esc_con_obs = asignaciones[asignaciones['observaciones'].notna() & (asignaciones['observaciones'] != '')]
escalas_tension = esc_con_obs['id_escala'].nunique()
pct_tension = escalas_tension / len(esc) * 100
print(f"\n  Escalas con tension de recursos: {escalas_tension} ({pct_tension:.1f}%)")

# Incidencias relacionadas con recursos
inc_recursos = incidencias[incidencias['tipo_incidencia'].isin([
    'averia de equipo', 'indisponibilidad de recurso por turno', 'falta de personal'
])]
print(f"  Incidencias relacionadas con recursos: {len(inc_recursos)} ({len(inc_recursos)/len(incidencias)*100:.1f}% del total)")

# ============================================================================
# 4. KPIs DE CUELLOS DE BOTELLA
# ============================================================================
print("\n" + "=" * 80)
print("4. KPIs DE CUELLOS DE BOTELLA")
print("=" * 80)

# 4.1 Frecuencia de cuellos de botella
# Definicion: dia en que hay >= 3 buques esperando simultaneamente
# Simplificado: dias con >= 3 escalas cuyo tiempo_espera > 4h
esc['fecha'] = esc['ata'].dt.date

dias_con_congestion = []
for fecha, grupo in esc.groupby('fecha'):
    esperas_altas = (grupo['tiempo_espera_h'] > 4).sum()
    if esperas_altas >= 2:
        dias_con_congestion.append({
            'fecha': fecha,
            'escalas_totales': len(grupo),
            'escalas_espera_alta': esperas_altas,
            'espera_media_dia': grupo['tiempo_espera_h'].mean(),
            'espera_max_dia': grupo['tiempo_espera_h'].max()
        })

df_congestion = pd.DataFrame(dias_con_congestion)
n_dias_cuello = len(df_congestion)
pct_dias_cuello = n_dias_cuello / 91 * 100
print(f"\n  Dias con cuello de botella (>=2 escalas con espera>4h): {n_dias_cuello} de 91 ({pct_dias_cuello:.1f}%)")
if len(df_congestion) > 0:
    print(f"  Espera media en dias congestionados: {df_congestion['espera_media_dia'].mean():.2f} h")
    print(f"  Espera maxima en dias congestionados: {df_congestion['espera_max_dia'].max():.2f} h")
    print(f"\n  Dias criticos:")
    for _, row in df_congestion.sort_values('espera_media_dia', ascending=False).head(10).iterrows():
        print(f"    {row['fecha']} | {row['escalas_totales']} escalas | {row['escalas_espera_alta']} con espera alta | media={row['espera_media_dia']:.1f}h | max={row['espera_max_dia']:.1f}h")

# 4.2 Indice de propagacion (retrasos en cascada)
# Escalas donde la espera se debe a muelle ocupado y la espera es > tiempo entre escalas programadas
escalas_cascada = esc[
    (esc['causa_espera'] == 'muelle ocupado') & (esc['tiempo_espera_h'] > 4)
]
idx_propagacion = len(escalas_cascada) / len(esc) * 100
print(f"\n  Indice de propagacion (espera>4h por muelle ocupado): {len(escalas_cascada)} escalas ({idx_propagacion:.1f}%)")

# 4.3 Concentracion horaria de la congestion
esc['hora_llegada'] = esc['ata'].dt.hour
espera_por_hora = esc.groupby('hora_llegada')['tiempo_espera_h'].agg(['mean', 'count']).round(2)
print(f"\n  --- Espera media por franja horaria de llegada ---")
franjas = [(0,6,'Madrugada 00-06'), (6,12,'Manana 06-12'), (12,18,'Tarde 12-18'), (18,24,'Noche 18-24')]
for h_ini, h_fin, nombre in franjas:
    mask = (esc['hora_llegada'] >= h_ini) & (esc['hora_llegada'] < h_fin)
    sub = esc[mask]
    if len(sub) > 0:
        print(f"  {nombre:20s}: {len(sub):3d} escalas | espera media = {sub['tiempo_espera_h'].mean():5.2f}h | mediana = {sub['tiempo_espera_h'].median():5.2f}h")

# 4.4 Analisis por dia de semana
esc['dia_semana'] = esc['ata'].dt.dayofweek
dias_nombre = {0:'Lunes',1:'Martes',2:'Miercoles',3:'Jueves',4:'Viernes',5:'Sabado',6:'Domingo'}
print(f"\n  --- Espera media por dia de la semana ---")
for d in range(7):
    sub = esc[esc['dia_semana'] == d]
    if len(sub) > 0:
        print(f"  {dias_nombre[d]:12s}: {len(sub):3d} escalas | espera media = {sub['tiempo_espera_h'].mean():5.2f}h | % espera>6h = {(sub['tiempo_espera_h']>6).mean()*100:5.1f}%")

# ============================================================================
# 5. TABLA RESUMEN DE KPIs
# ============================================================================
print("\n" + "=" * 80)
print("5. TABLA RESUMEN DE KPIs - ESCENARIO BASE")
print("=" * 80)

kpis_resumen = pd.DataFrame({
    'KPI': [
        'Tiempo medio de espera (AWT)',
        'Mediana de espera',
        'Tiempo medio de servicio (AST)',
        'Tiempo medio de estancia (ATT)',
        'Ratio de espera (WTR)',
        '% escalas con espera > 6h',
        '% escalas con espera > 24h',
        'Desviacion absoluta media ETA',
        'BOR global',
        'BOR Muelle Norte',
        'BOR Muelle Sur',
        'BOR Muelle Este',
        'BOR Muelle Oeste',
        'BOR Muelle Ro-Ro',
        'Indice compatibilidad buque-muelle',
        'Recursos medios por escala',
        'Tasa utilizacion gruas (global)',
        '% escalas con tension recursos',
        '% escalas con incidencia',
        'Dias con cuello de botella',
        'Indice de propagacion',
    ],
    'Valor': [
        f'{awt:.2f} h',
        f'{awt_mediana:.2f} h',
        f'{ast_val:.2f} h',
        f'{att:.2f} h',
        f'{wtr_global:.3f}',
        f'{pct_espera_6h:.1f}%',
        f'{pct_espera_24h:.1f}%',
        f'{desv_abs_media:.2f} h',
        f'{bor_global:.1f}%',
        f'{bor_muelles[1]:.1f}%',
        f'{bor_muelles[2]:.1f}%',
        f'{bor_muelles[3]:.1f}%',
        f'{bor_muelles[4]:.1f}%',
        f'{bor_muelles[5]:.1f}%',
        f'{idx_compat:.1f}%',
        f'{recursos_por_escala.mean():.1f}',
        f'{tasa_gruas_global:.1f}%',
        f'{pct_tension:.1f}%',
        f'{incidencias["id_escala"].nunique() / len(esc) * 100:.1f}%',
        f'{n_dias_cuello} de 91 ({pct_dias_cuello:.1f}%)',
        f'{idx_propagacion:.1f}%',
    ],
    'Referencia': [
        '< 3h deseable',
        '< 1h deseable',
        'Variable por tipo',
        'Minimizar',
        '< 0.30 aceptable',
        '< 10% deseable',
        '< 3% deseable',
        '< 3h aceptable',
        '40-60% optimo',
        '< 65% sin congestion',
        '< 65% sin congestion',
        '< 65% sin congestion',
        '< 65% sin congestion',
        '< 65% sin congestion',
        '> 90% deseable',
        'Variable',
        '> 50% eficiente',
        '< 10% deseable',
        '< 20% deseable',
        '< 5% deseable',
        '< 5% deseable',
    ],
    'Diagnostico': [
        '⚠ Por encima del rango deseable' if awt > 3 else '✓ Aceptable',
        '✓ Aceptable' if awt_mediana < 1 else '⚠ Revisar',
        'Referencia',
        'Referencia',
        '✓ Dentro del rango' if wtr_global < 0.3 else '⚠ Superado',
        '⚠ Superado' if pct_espera_6h > 10 else '✓ Aceptable',
        '⚠ Superado' if pct_espera_24h > 3 else '✓ Aceptable',
        '✓ Aceptable' if desv_abs_media < 3 else '⚠ Revisar',
        '✓ Rango adecuado' if 35 < bor_global < 60 else '⚠ Revisar',
        '⚠ Cerca del limite' if bor_muelles[1] > 55 else '✓ Aceptable',
        '✓ Aceptable',
        '✓ Aceptable',
        '✓ Aceptable' if bor_muelles[4] < 55 else '⚠ Moderado',
        '↓ Infrautilizado' if bor_muelles[5] < 20 else '✓ Aceptable',
        '✓ Aceptable' if idx_compat > 90 else '⚠ Mejorable',
        'Referencia',
        '⚠ Bajo' if tasa_gruas_global < 40 else '✓ Aceptable',
        '✓ Aceptable' if pct_tension < 10 else '⚠ Revisar',
        '⚠ Superado' if incidencias['id_escala'].nunique()/len(esc)*100 > 20 else '✓ Aceptable',
        '⚠ Frecuente' if pct_dias_cuello > 10 else '✓ Aceptable',
        '⚠ Significativo' if idx_propagacion > 5 else '✓ Aceptable',
    ]
})

print(kpis_resumen.to_string(index=False))

# Guardar tabla resumen
kpis_resumen.to_csv(RUTA + 'KPIs_resumen_escenario_base.csv', index=False, encoding='utf-8-sig')

# ============================================================================
# 6. GRAFICOS
# ============================================================================
print("\n\nGenerando graficos...")

# --- Fig 1: Distribucion de tiempos de espera ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(esc['tiempo_espera_h'], bins=30, edgecolor='black', alpha=0.7, color='#4C72B0')
axes[0].axvline(awt, color='red', linestyle='--', label=f'Media = {awt:.1f}h')
axes[0].axvline(awt_mediana, color='orange', linestyle='--', label=f'Mediana = {awt_mediana:.1f}h')
axes[0].set_xlabel('Tiempo de espera (horas)')
axes[0].set_ylabel('Frecuencia')
axes[0].set_title('Distribución de tiempos de espera')
axes[0].legend()

# Box plot por tipo de buque
tipos_orden = ['granelero', 'carga general', 'tanque', 'portacontenedores', 'ro-ro']
esc['tipo_buque_cat'] = pd.Categorical(esc['tipo_buque'], categories=tipos_orden, ordered=True)
sns.boxplot(data=esc, x='tipo_buque_cat', y='tiempo_espera_h', ax=axes[1])
axes[1].set_xlabel('Tipo de buque')
axes[1].set_ylabel('Tiempo de espera (horas)')
axes[1].set_title('Tiempo de espera por tipo de buque')
axes[1].tick_params(axis='x', rotation=20)
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig01_distribucion_espera.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 2: Tiempos de servicio por tipo ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.boxplot(data=esc, x='tipo_buque_cat', y='tiempo_servicio_h', ax=axes[0])
axes[0].set_xlabel('Tipo de buque')
axes[0].set_ylabel('Tiempo de servicio (horas)')
axes[0].set_title('Tiempo de servicio por tipo de buque')
axes[0].tick_params(axis='x', rotation=20)

sns.boxplot(data=esc, x='tipo_buque_cat', y='tiempo_total_h', ax=axes[1])
axes[1].set_xlabel('Tipo de buque')
axes[1].set_ylabel('Tiempo total de estancia (horas)')
axes[1].set_title('Tiempo total de estancia por tipo de buque')
axes[1].tick_params(axis='x', rotation=20)
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig02_tiempos_servicio.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 3: BOR por muelle ---
fig, ax = plt.subplots(figsize=(10, 5))
nombres = [nombres_muelles[i] for i in range(1, 6)]
bors = [bor_muelles[i] for i in range(1, 6)]
colores = ['#e74c3c' if b > 65 else '#f39c12' if b > 55 else '#27ae60' if b > 20 else '#95a5a6' for b in bors]
bars = ax.bar(nombres, bors, color=colores, edgecolor='black', alpha=0.8)
ax.axhline(65, color='red', linestyle='--', alpha=0.7, label='Umbral congestion (65%)')
ax.axhline(40, color='green', linestyle='--', alpha=0.5, label='Umbral minimo eficiente (40%)')
ax.set_ylabel('Tasa de ocupacion (%)')
ax.set_title('Tasa de Ocupación de Muelles (BOR) - Escenario Base')
ax.legend()
ax.set_ylim(0, 80)
for bar, val in zip(bars, bors):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.1f}%',
            ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig03_bor_muelles.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 4: Causas de espera ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
causas = esc['causa_espera'].value_counts()
causas.plot(kind='barh', ax=axes[0], color='#4C72B0', edgecolor='black')
axes[0].set_xlabel('Numero de escalas')
axes[0].set_title('Distribución de causas de espera')

# Incidencias por tipo
inc_tipos = incidencias['tipo_incidencia'].value_counts()
inc_tipos.plot(kind='barh', ax=axes[1], color='#DD8452', edgecolor='black')
axes[1].set_xlabel('Numero de incidencias')
axes[1].set_title('Distribución de incidencias por tipo')
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig04_causas_incidencias.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 5: Evolucion temporal de esperas ---
fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# Media movil semanal de esperas
esc_sorted = esc.sort_values('ata')
esc_sorted['espera_movil_7d'] = esc_sorted['tiempo_espera_h'].rolling(window=14, min_periods=3).mean()
axes[0].plot(esc_sorted['ata'], esc_sorted['tiempo_espera_h'], 'o', alpha=0.3, markersize=4, label='Espera individual')
axes[0].plot(esc_sorted['ata'], esc_sorted['espera_movil_7d'], '-', color='red', linewidth=2, label='Media movil (14 escalas)')
axes[0].set_ylabel('Tiempo de espera (h)')
axes[0].set_title('Evolución temporal de tiempos de espera')
axes[0].legend()
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
axes[0].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))

# Escalas por semana
esc['semana'] = esc['ata'].dt.isocalendar().week.astype(int)
escalas_semana = esc.groupby('semana').agg(
    n_escalas=('id_escala', 'count'),
    espera_media=('tiempo_espera_h', 'mean')
)
ax2 = axes[1]
ax2.bar(escalas_semana.index, escalas_semana['n_escalas'], alpha=0.6, color='#4C72B0', label='Escalas/semana')
ax2_twin = ax2.twinx()
ax2_twin.plot(escalas_semana.index, escalas_semana['espera_media'], 'o-', color='red', label='Espera media')
ax2.set_xlabel('Semana del año')
ax2.set_ylabel('Numero de escalas')
ax2_twin.set_ylabel('Espera media (h)')
ax2.set_title('Actividad semanal y espera media')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig05_evolucion_temporal.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 6: Heatmap hora x dia de semana ---
fig, ax = plt.subplots(figsize=(12, 5))
tabla_hora_dia = esc.groupby(['dia_semana', 'hora_llegada'])['tiempo_espera_h'].mean().unstack(fill_value=0)
# Rellenar horas faltantes
for h in range(24):
    if h not in tabla_hora_dia.columns:
        tabla_hora_dia[h] = 0
tabla_hora_dia = tabla_hora_dia.reindex(columns=range(24), fill_value=0)
tabla_hora_dia.index = [dias_nombre[d] for d in tabla_hora_dia.index]
sns.heatmap(tabla_hora_dia, cmap='YlOrRd', ax=ax, linewidths=0.5,
            cbar_kws={'label': 'Espera media (h)'})
ax.set_xlabel('Hora del dia')
ax.set_ylabel('Dia de la semana')
ax.set_title('Mapa de calor: espera media por hora y dia de la semana')
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig06_heatmap_espera.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 7: Scatter espera vs volumen ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for tipo in tipos_orden:
    sub = esc[esc['tipo_buque'] == tipo]
    axes[0].scatter(sub['volumen_carga_t'], sub['tiempo_espera_h'], alpha=0.5, label=tipo, s=30)
axes[0].set_xlabel('Volumen de carga (t)')
axes[0].set_ylabel('Tiempo de espera (h)')
axes[0].set_title('Tiempo de espera vs. Volumen de carga')
axes[0].legend(fontsize=8)

for tipo in tipos_orden:
    sub = esc[esc['tipo_buque'] == tipo]
    axes[1].scatter(sub['volumen_carga_t'], sub['tiempo_servicio_h'], alpha=0.5, label=tipo, s=30)
axes[1].set_xlabel('Volumen de carga (t)')
axes[1].set_ylabel('Tiempo de servicio (h)')
axes[1].set_title('Tiempo de servicio vs. Volumen de carga')
axes[1].legend(fontsize=8)
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig07_scatter_volumen.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Fig 8: Prioridad y espera ---
fig, ax = plt.subplots(figsize=(8, 5))
orden_prio = ['alta', 'media', 'baja']
esc['prioridad_cat'] = pd.Categorical(esc['prioridad'], categories=orden_prio, ordered=True)
sns.boxplot(data=esc, x='prioridad_cat', y='tiempo_espera_h', ax=ax, palette=['#27ae60','#f39c12','#e74c3c'])
ax.set_xlabel('Prioridad')
ax.set_ylabel('Tiempo de espera (h)')
ax.set_title('Tiempo de espera según prioridad de la escala')
plt.tight_layout()
plt.savefig(RUTA_FIG + 'fig08_prioridad_espera.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"\nGraficos guardados en: {RUTA_FIG}")
print("  fig01_distribucion_espera.png")
print("  fig02_tiempos_servicio.png")
print("  fig03_bor_muelles.png")
print("  fig04_causas_incidencias.png")
print("  fig05_evolucion_temporal.png")
print("  fig06_heatmap_espera.png")
print("  fig07_scatter_volumen.png")
print("  fig08_prioridad_espera.png")
print("\n" + "=" * 80)
print("ANALISIS COMPLETADO")
print("=" * 80)
