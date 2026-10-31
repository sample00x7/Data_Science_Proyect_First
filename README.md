# Mercado Inmobiliario Digital en Diez de Octubre, La Habana

## Historia del proyecto

Este proyecto responde a una pregunta sencilla: **¿Cuánto cuesta realmente vivir en el municipio Diez de Octubre, La Habana?**

Una persona que quiera comprar o alquilar una vivienda en esa zona no tiene una referencia clara de precios ni de qué tipo de inmuebles están disponibles en el mercado digital. Con este trabajo caracterizo el mercado inmobiliario local usando:

1. Anuncios reales publicados en línea (Revolico).
2. Datos oficiales del Anuario Estadístico de Cuba (ONEI) como contexto general.

El objetivo es ofrecer una guía clara, sin tecnicismos, para cualquier persona interesada en comprar o alquilar vivienda en Diez de Octubre: cuánto cuesta, en qué zona, qué características afectan el precio y en qué moneda se declaran los anuncios.

## Objetivos

- Analizar la oferta inmobiliaria publicada en plataformas digitales cubanas enfocada al municipio Diez de Octubre.
- Caracterizar precios, tipos de inmueble, zonas, moneda declarada y características físicas.
- Responder 30 preguntas de investigación coherentes entre sí, comunicables a personas sin conocimientos técnicos ni del tema inmobiliario.
- Proporcionar una base replicable y abierta para futuros análisis del mercado digital cubano.

## Fuentes de datos

| Fuente | Aporte |
|--------|--------|
| **Revolico** (scraping propio) | Anuncios actuales de inmobiliaria en Diez de Octubre: precios, tipos, zonas, moneda. |
| **Anuario Estadístico de Cuba (ONEI)** | Contexto oficial: población, vivienda y tenencia del municipio para enmarcar la muestra digital. |
| **Otras fuentes con concurrencia y validez** | Solo se usan si aportan datos públicos y verificables del mercado informal cubano. |

> Nota: Este proyecto no aborda aspectos políticos ni hace comparativas que no sean directamente hacia el mercado inmobiliario.

## Estructura del repositorio

```
mercado-digital-cubano-en-10-de-octubre/
├── README.md                                      # Historia, objetivos, fuentes y estructura
├── datos/brutos/revolico_crudos.json       # Anuncios originales de Revolico (101)
├── datos/brutos/revolico_crudos_actualizados.json  # Anuncios verificados y actualizados (93)
├── datos/brutos/revolico_crudos_con_fechas.json    # Con fechas de publicación (proxy por ID)
├── datos/brutos/revolico_crudos_ordenado_por_id.json # Ordenado por antigüedad (ID)
├── datos/limpios/datos_unificados_facebook_revolico.json  # 120 anuncios (FB + Revolico)
├── datos/limpios/LISTA_ANOMALIAS_POR_ANUNCIO.txt   # Anomalías por anuncio
├── datos/limpios/LIMPIEZA_POR_TIEMPO_DE_PUBLICACION.txt # Limpieza por antigüedad
├── datos/limpios/anuncios_activos.txt       # 80 anuncios activos
├── datos/limpios/anuncios_inactivos.txt     # 21 anuncios inactivos
├── datos/limpios/nuevos_anuncios.txt        # 13 anuncios nuevos encontrados
├── datos/limpios/reporte_actualizacion_anuncios.txt # Reporte de actualización
├── datos/limpios/reporte_limpieza_fechas.txt # Reporte de limpieza por fechas
├── src/scrape_revolico.py             # Script de descarga de anuncios (Revolico)
├── scripts/agregar_permuta.py         # Detección de permutas en títulos
├── scripts/verificar_y_actualizar_anuncios.py  # Verificar anuncios activos + nuevos
├── scripts/extraer_fechas_publicacion.py   # Extraer fechas de publicación
├── scripts/mezclar_facebook_revolico.py    # Mezclar Facebook + Revolico
├── scripts/analizar_30_preguntas.py    # Analizar y responder las 30 preguntas
├── analisis/generar_informe_bloque1.py # Script para generar informe del Bloque 1
├── analisis/informe_final.md          # 30 preguntas respondidas
├── analisis/telefonos_y_enlaces.txt   # Teléfonos y enlaces de anuncios
├── analisis/limpieza/explicacion_datos_sospechosos.txt
├── analisis/limpieza/LISTA_PARA_LIMPIAR_MANUAL.txt
├── fuentes/anuario_estadistico_notas.md # Notas de fuentes oficiales consultadas
├── requirements.txt                   # Dependencias de Python
└── LICENSE                            # Licencia MIT
```

## Las 30 preguntas de investigación

Todas apuntan al mismo objetivo: entender el mercado inmobiliario digital de Diez de Octubre. Están organizadas en 6 bloques temáticos y son coherentes entre sí.

### Bloque A: Precios del mercado (6)
1. ¿Cuál es el precio promedio de venta en USD en Diez de Octubre?
2. ¿Cuál es el precio mediano de alquiler en USD?
3. ¿Cuál es el rango de precios que cubre el 80% de los anuncios de venta?
4. ¿Cuál es el anuncio de venta más caro y el más barato publicado?
5. ¿Qué proporción de anuncios no declara precio?
6. ¿Existe diferencia significativa entre el precio promedio de venta y el de alquiler?

### Bloque B: Tipos de inmueble (6)
7. ¿Cuáles son los tipos de inmueble más publicados? (casa, apartamento, local, terreno)
8. ¿Qué porcentaje son casas independientes frente a apartamentos?
9. ¿Cuál es el precio promedio de venta por tipo de inmueble?
10. ¿Qué tipo de inmueble concentra el precio máximo declarado?
11. ¿Cuántos anuncios son de venta frente a cuántos son de alquiler?
12. ¿Qué tipo de inmueble domina en las zonas con precios más altos?

### Bloque C: Características físicas (6)
13. ¿Cuál es la cantidad más común de cuartos/habitaciones?
14. ¿Cómo varía el precio según el número de cuartos?
15. ¿Qué porcentaje de anuncios menciona garaje y cómo afecta al precio?
16. ¿Cuántos anuncios especifican "planta baja" y cuál es su precio promedio?
17. ¿Qué porcentaje menciona metraje (m²) y cuál es el promedio?
18. ¿Qué características físicas se mencionan con más frecuencia? (patio, azotea, cocina, etc.)

### Bloque D: Ubicación dentro de Diez de Octubre (6)
19. ¿Qué zonas o barrios aparecen con más frecuencia en los anuncios? (Santos Suárez, La Víbora, Lawton, Luyano, El Sevillano, etc.)
20. ¿Qué zona tiene el precio promedio de venta más alto?
21. ¿Qué zona tiene la mayor cantidad de anuncios publicados?
22. ¿Hay diferencia de precios entre zonas dentro del mismo municipio?
23. ¿Qué zonas aparecen solo en venta o solo en alquiler?
24. ¿Cuántos anuncios no especifican zona dentro del municipio?

### Bloque E: Moneda y mercado informal (6)
25. ¿Qué proporción de anuncios declara precios en USD frente a CUP?
26. ¿Cuál es el precio promedio de los anuncios declarados en CUP?
27. ¿Qué porcentaje de anuncios incluye palabras como "oportunidad", "ganga" o "permuta"?
28. ¿Qué rango de precios es más frecuente para ventas en USD?
29. ¿Cuántos anuncios parecen ser de particulares frente a posibles anuncios repetidos o agencias (por lenguaje o título)?
30. ¿Qué recomendación práctica se puede hacer a alguien que quiera comprar o alquilar en Diez de Octubre según estos datos?

## Cómo ejecutar el scraping y análisis

Desde la carpeta raíz del proyecto:

```bash
# Requerimientos
pip install -r requirements.txt

# 1. Descargar anuncios de Revolico (guardado en datos/brutos/)
python3 src/scrape_revolico.py

# 2. Verificar anuncios activos y agregar nuevos de Diez de Octubre
python3 scripts/verificar_y_actualizar_anuncios.py

# 3. Extraer fechas de publicación (proxy por ID de enlace)
python3 scripts/extraer_fechas_publicacion.py

# 4. Marcar permutas en los archivos brutos
python3 scripts/agregar_permuta.py

# 5. Mezclar datos de Revolico y Facebook en estructura unificada
python3 scripts/mezclar_facebook_revolico.py

# 6. Analizar y responder las 30 preguntas de investigación
python3 scripts/analizar_30_preguntas.py
```

Los resultados se guardan en:
- `datos/brutos/revolico_crudos_actualizados.json` (anuncios verificados)
- `datos/brutos/revolico_crudos_con_fechas.json` (con fechas de publicación)
- `datos/brutos/revolico_crudos_ordenado_por_id.json` (ordenado por antigüedad)
- `datos/limpios/datos_unificados_facebook_revolico.json` (120 anuncios: FB + Revolico)
- `datos/limpios/anuncios_activos.txt`
- `datos/limpios/anuncios_inactivos.txt`
- `datos/limpios/nuevos_anuncios.txt`
- `analisis/informe_final.md` (30 preguntas respondidas)

## Herramientas utilizadas

- **Python** con `requests` y `BeautifulSoup` para el scraping.
- **Pandas** y **Matplotlib/Seaborn** para el análisis y visualizaciones.
- No se usan Excel, SQL ni Power BI.
- Todas las dependencias están en `requirements.txt`.

## Limitaciones

- Los datos provienen únicamente de anuncios publicados en un portal digital; no representan la totalidad del mercado físico.
- Algunos anuncios no declaran precio ni ubicación específica dentro del municipio.
- La detección de municipio se basa en palabras clave presentes en el título y el enlace del anuncio.

## Exposición

El proyecto incluye materiales para una exposición de aproximadamente 5-10 minutos, pensada para personas sin conocimientos técnicos ni del tema inmobiliario. Se recomienda presentar:
1. El problema: ¿cuánto cuesta vivir en Diez de Octubre?
2. La fuente: anuncios reales de Revolico + contexto del Anuario Estadístico.
3. Los 3 hallazgos más importantes (precio promedio, zona más cara, tipo más común).
4. Qué significa esto para una persona común.
5. Limitaciones de los datos.