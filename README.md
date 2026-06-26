generar_dataset.py (1000 líneas)	Crea la terminal sintética: genera muelles, buques, recursos, las 180 escalas con sus tiempos, incidencias…	Los CSV con los datos simulados

analisis_kpis.py (585 líneas)	Lee esos datos y calcula los KPIs del escenario base.	El diagnóstico: AWT 5,57 h, BOR 37,4 %, etc.

simulacion_dss.py (687 líneas)	Aplica las reglas de los 5 módulos sobre las escalas y recalcula los KPIs.	El escenario mejorado: AWT 3,22 h → el −42,3 %

multisim_dss.py (260 líneas)	Repite la simulación 50 veces con aleatoriedad.	El rango de robustez: media 25 % (16-33 %)

Se uso claude para escribir y arreglar los codigos para que hicieran run correctamente. Mas alla se le dio reglas muy especificas a Claude de no cambiar el concepto y ciertas reglas.
