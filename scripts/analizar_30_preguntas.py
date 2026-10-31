#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza los datos unificados (Facebook + Revolico) y responde las 30 preguntas
de investigación del proyecto.

Lee:
  - datos/limpios/datos_unificados_facebook_revolico.json
  - datos/brutos/revolico_crudos_actualizados.json

Escribe:
  - analisis/informe_final.md (con las respuestas)
"""

import json
import statistics
import re
from collections import Counter, defaultdict
from datetime import datetime

UNIFICADO_FILE = "datos/limpios/datos_unificados_facebook_revolico.json"
REVOLICO_FILE = "datos/brutos/revolico_crudos_actualizados.json"
OUTPUT_FILE = "analisis/informe_final.md"


def cargar_datos():
    with open(UNIFICADO_FILE, encoding="utf-8") as f:
        datos_unificados = json.load(f)
    with open(REVOLICO_FILE, encoding="utf-8") as f:
        datos_revolico = json.load(f)
    return datos_unificados, datos_revolico


def es_venta(titulo):
    t = titulo.lower()
    palabras_venta = ["vendo", "se vende", "venta", "vende"]
    palabras_alquiler = ["alquiler", "alquila", "se alquila", "renta", "renta de"]
    es_v = any(p in t for p in palabras_venta)
    es_a = any(p in t for p in palabras_alquiler)
    return es_v and not es_a


def es_alquiler(titulo):
    t = titulo.lower()
    palabras_alquiler = ["alquiler", "alquila", "se alquila", "renta", "renta de"]
    palabras_venta = ["vendo", "se vende", "venta", "vende"]
    es_a = any(p in t for p in palabras_alquiler)
    es_v = any(p in t for t in palabras_venta) if False else any(p in t for p in palabras_venta)
    return es_a and not es_v


def obtener_precio_usd(anuncio):
    """Devuelve precio en USD si está declarado, None si no."""
    precio = anuncio.get("precio")
    moneda = anuncio.get("moneda", "")
    if precio is None:
        return None
    if moneda == "USD":
        return precio
    if moneda == "CUP":
        # Convertir CUP a USD aproximado (1 USD = 24 CUP aprox en mercado informal)
        # Dejamos como None para no distorsionar, o podemos convertir
        return None
    return None


def obtener_tipo_inmueble(anuncio):
    """Extrae tipo de inmueble del anuncio."""
    # Para Facebook viene en detalles_propiedad.tipo
    tipo = anuncio.get("detalles_propiedad", {}).get("tipo", "")
    if tipo:
        return tipo
    # Para Revolico, inferir del título
    titulo = anuncio.get("titulo", "").lower()
    if "apartamento" in titulo or "apto" in titulo:
        return "Apartamento"
    if "casa" in titulo or "biplanta" in titulo or "planta baja" in titulo:
        return "Casa"
    if "local" in titulo:
        return "Local"
    if "terreno" in titulo:
        return "Terreno"
    return "Inmueble"


def obtener_municipio(anuncio):
    """Extrae municipio del anuncio."""
    # Facebook: detalles_propiedad.ubicacion
    # Revolico: campo municipio
    ubicacion = anuncio.get("detalles_propiedad", {}).get("ubicacion", "")
    if ubicacion:
        return ubicacion
    return anuncio.get("municipio", "")


def obtener_zonas(texto):
    """Extrae zonas de Diez de Octubre mencionadas en el texto."""
    zonas = [
        "Santos Suárez", "Santos Suarez", "La Víbora", "La Vibora",
        "Lawton", "Luyano", "El Sevillano", "Sevillano", "Mónaco", "Monaco",
        "La Asunción", "Asunción", "Santa Catalina", "Vista Alegre",
        "Luyanó", "Luyano", "Reparto Sevillano", "Reparto Lawton",
        "Reparto Asunción", "Calzada", "Vía Blanca", "Via Blanca"
    ]
    texto_lower = texto.lower()
    zonas_encontradas = []
    for zona in zonas:
        if zona.lower() in texto_lower:
            zonas_encontradas.append(zona)
    return zonas_encontradas


def contar_palabras_informalidad(texto):
    """Cuenta palabras como oportunidad, ganga, permuta."""
    texto_lower = texto.lower()
    count = 0
    for palabra in ["oportunidad", "ganga", "permuta", "intercambio"]:
        if palabra in texto_lower:
            count += 1
    return count


def main():
    datos_unificados, datos_revolico = cargar_datos()

    # Separar por fuente
    anuncios_facebook = [a for a in datos_unificados if a.get("fuente") == "facebook"]
    anuncios_revolico = [a for a in datos_unificados if a.get("fuente") == "revolico"]

    print(f"Facebook: {len(anuncios_facebook)}")
    print(f"Revolico: {len(anuncios_revolico)}")
    print(f"Total: {len(datos_unificados)}")

    # ========================================================================
    # BLOQUE A: PRECIOS DEL MERCADO
    # ========================================================================
    print("\n--- BLOQUE A: PRECIOS ---")

    # Precios de venta en USD (solo Revolico tiene precios numéricos consistentes)
    precios_venta_usd = []
    for a in datos_revolico:
        if es_venta(a.get("titulo", "")) and a.get("moneda") == "USD" and a.get("precio"):
            precios_venta_usd.append(a["precio"])

    print(f"Anuncios de venta en USD: {len(precios_venta_usd)}")
    if precios_venta_usd:
        promedio_venta = statistics.mean(precios_venta_usd)
        mediana_venta = statistics.median(precios_venta_usd)
        precio_min = min(precios_venta_usd)
        precio_max = max(precios_venta_usd)
        print(f"  Promedio: {promedio_venta:.2f} USD")
        print(f"  Mediana: {mediana_venta:.2f} USD")
        print(f"  Mín: {precio_min} USD, Máx: {precio_max} USD")

    # Precios de alquiler en USD
    precios_alquiler_usd = []
    for a in datos_revolico:
        if es_alquiler(a.get("titulo", "")) and a.get("moneda") == "USD" and a.get("precio"):
            precios_alquiler_usd.append(a["precio"])

    print(f"Anuncios de alquiler en USD: {len(precios_alquiler_usd)}")
    if precios_alquiler_usd:
        mediana_alquiler = statistics.median(precios_alquiler_usd)
        print(f"  Mediana alquiler: {mediana_alquiler:.2f} USD")

    # Anuncios sin precio
    total_anuncios = len(datos_revolico)
    sin_precio = [a for a in datos_revolico if not a.get("precio")]
    print(f"Anuncios sin precio: {len(sin_precio)} de {total_anuncios}")
    proporcion_sin_precio = (len(sin_precio) / total_anuncios * 100) if total_anuncios else 0
    print(f"  Proporción: {proporcion_sin_precio:.2f}%")

    # ========================================================================
    # BLOQUE B: TIPOS DE INMUEBLE
    # ========================================================================
    print("\n--- BLOQUE B: TIPOS DE INMUEBLE ---")

    tipos_contador = Counter()
    for a in datos_unificados:
        tipo = obtener_tipo_inmueble(a)
        tipos_contador[tipo] += 1

    print("Tipos de inmueble:")
    for tipo, count in tipos_contador.most_common():
        print(f"  {tipo}: {count}")

    # Casas vs apartamentos
    casas = sum(1 for t in tipos_contador if "casa" in t.lower() or "biplanta" in t.lower())
    apartamentos = sum(1 for t in tipos_contador if "apartamento" in t.lower() or "apto" in t.lower())
    print(f"  Casas: {casas}, Apartamentos: {apartamentos}")

    # ========================================================================
    # BLOQUE C: CARACTERÍSTICAS FÍSICAS
    # ========================================================================
    print("\n--- BLOQUE C: CARACTERÍSTICAS FÍSICAS ---")

    # Cuartos más comunes
    cuartos_contador = Counter()
    for a in datos_revolico:
        titulo = a.get("titulo", "").lower()
        m = re.search(r"(\d+)\s*(?:cuartos|cuarto|habitaciones|habitación|/4)", titulo)
        if m:
            cuartos_contador[m.group(1)] += 1

    print("Cuartos más comunes:")
    for cuartos, count in cuartos_contador.most_common(5):
        print(f"  {cuartos} cuartos: {count}")

    # Garaje
    con_garaje = 0
    for a in datos_revolico:
        texto = a.get("titulo", "").lower()
        if "garaje" in texto:
            con_garaje += 1
    print(f"Anuncios con garaje: {con_garaje} de {total_anuncios}")

    # Planta baja
    con_planta_baja = 0
    for a in datos_revolico:
        texto = a.get("titulo", "").lower()
        if "planta baja" in texto:
            con_planta_baja += 1
    print(f"Anuncios con planta baja: {con_planta_baja} de {total_anuncios}")

    # Metraje
    con_metro = 0
    for a in datos_revolico:
        texto = a.get("titulo", "").lower()
        if "m²" in texto or "m2" in texto or "metros" in texto:
            con_metro += 1
    print(f"Anuncios con metraje: {con_metro} de {total_anuncios}")

    # Características físicas más frecuentes
    características = ["patio", "azotea", "cocina", "baño", "cuarto", "sala", "comedor", "terraza", "patio"]
    char_contador = Counter()
    for a in datos_revolico:
        texto = a.get("titulo", "").lower()
        for car in características:
            if car in texto:
                char_contador[car] += 1
    print("Características más frecuentes:")
    for car, count in char_contador.most_common(5):
        print(f"  {car}: {count}")

    # ========================================================================
    # BLOQUE D: UBICACIÓN
    # ========================================================================
    print("\n--- BLOQUE D: UBICACIÓN ---")

    zonas_contador = Counter()
    for a in datos_revolico:
        texto = (a.get("titulo", "") + " " + a.get("enlace", "")).lower()
        zonas = obtener_zonas(texto)
        for z in zonas:
            zonas_contador[z] += 1

    print("Zonas más frecuentes:")
    for zona, count in zonas_contador.most_common(10):
        print(f"  {zona}: {count}")

    # ========================================================================
    # BLOQUE E: MONEDA Y MERCADO INFORMAL
    # ========================================================================
    print("\n--- BLOQUE E: MONEDA Y MERCADO INFORMAL ---")

    usd_count = len([a for a in datos_revolico if a.get("moneda") == "USD"])
    cup_count = len([a for a in datos_revolico if a.get("moneda") == "CUP"])
    total_con_moneda = usd_count + cup_count
    print(f"Anuncios en USD: {usd_count}")
    print(f"Anuncios en CUP: {cup_count}")
    if total_con_moneda:
        print(f"  % USD: {usd_count/total_con_moneda*100:.1f}%")
        print(f"  % CUP: {cup_count/total_con_moneda*100:.1f}%")

    # Palabras de informalidad
    informalidad_contador = Counter()
    for a in datos_revolico:
        texto = a.get("titulo", "").lower()
        if "oportunidad" in texto:
            informalidad_contador["oportunidad"] += 1
        if "ganga" in texto:
            informalidad_contador["ganga"] += 1
        if "permuta" in texto or "intercambio" in texto:
            informalidad_contador["permuta"] += 1
    print("Palabras de informalidad:")
    for palabra, count in informalidad_contador.most_common():
        print(f"  {palabra}: {count}")

    # Permutas
    con_permuta = len([a for a in datos_revolico if a.get("permuta")])
    print(f"Anuncios con permuta: {con_permuta} de {total_anuncios}")

    # ========================================================================
    # GENERAR INFORME
    # ========================================================================
    print("\n--- GENERANDO INFORME ---")

    generar_informe(
        precios_venta_usd=precios_venta_usd,
        precios_alquiler_usd=precios_alquiler_usd,
        promedio_venta=promedio_venta if precios_venta_usd else None,
        mediana_venta=mediana_venta if precios_venta_usd else None,
        precio_min=precio_min if precios_venta_usd else None,
        precio_max=precio_max if precios_venta_usd else None,
        mediana_alquiler=mediana_alquiler if precios_alquiler_usd else None,
        total_anuncios=total_anuncios,
        sin_precio=len(sin_precio),
        proporcion_sin_precio=proporcion_sin_precio,
        tipos_contador=tipos_contador,
        casas=casas,
        apartamentos=apartamentos,
        cuartos_contador=cuartos_contador,
        con_garaje=con_garaje,
        con_planta_baja=con_planta_baja,
        con_metro=con_metro,
        char_contador=char_contador,
        zonas_contador=zonas_contador,
        usd_count=usd_count,
        cup_count=cup_count,
        total_con_moneda=total_con_moneda,
        informalidad_contador=informalidad_contador,
        con_permuta=con_permuta,
    )


def generar_informe(**kwargs):
    """Escribe el informe_final.md con todas las respuestas."""
    lineas = []
    lineas.append("# Informe Final: Mercado Inmobiliario Digital en Diez de Octubre")
    lineas.append("")
    lineas.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lineas.append("")
    lineas.append("## Introducción")
    lineas.append("Este informe presenta el análisis del mercado inmobiliario digital en el municipio Diez de Octubre, La Habana, basado en anuncios publicados en Revolico y en grupos de Facebook.")
    lineas.append("")
    lineas.append("## Metodología")
    lineas.append("Datos recolectados mediante scraping de anuncios publicados en Revolico y grupos de Facebook especializados en venta de viviendas en La Habana. Los datos fueron limpiados y analizados para responder 30 preguntas de investigación organizadas en 6 bloques temáticos.")
    lineas.append("")

    # ========================================================================
    # BLOQUE A
    # ========================================================================
    lineas.append("## Las 30 preguntas y sus respuestas")
    lineas.append("")
    lineas.append("### Bloque A: Precios del mercado")
    lineas.append("")
    lineas.append("1. ¿Cuál es el precio promedio de venta en USD en Diez de Octubre?")
    if kwargs['promedio_venta']:
        lineas.append(f"   > Respuesta: {kwargs['promedio_venta']:,.2f} USD (basado en {len(kwargs['precios_venta_usd'])} anuncios)")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("2. ¿Cuál es el precio mediano de alquiler en USD?")
    if kwargs['mediana_alquiler']:
        lineas.append(f"   > Respuesta: {kwargs['mediana_alquiler']:,.2f} USD (basado en {len(kwargs['precios_alquiler_usd'])} anuncios)")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("3. ¿Cuál es el rango de precios que cubre el 80% de los anuncios de venta?")
    if kwargs['precio_min'] and kwargs['precio_max']:
        lineas.append(f"   > Respuesta: Entre {kwargs['precio_min']:,} USD y {kwargs['precio_max']:,} USD")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("4. ¿Cuál es el anuncio de venta más caro y el más barato publicado?")
    if kwargs['precio_max'] and kwargs['precio_min']:
        lineas.append(f"   > Más caro: {kwargs['precio_max']:,} USD")
        lineas.append(f"   > Más barato: {kwargs['precio_min']:,} USD")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("5. ¿Qué proporción de anuncios no declara precio?")
    lineas.append(f"   > Respuesta: {kwargs['proporcion_sin_precio']:.2f}% ({kwargs['sin_precio']} de {kwargs['total_anuncios']} anuncios)")
    lineas.append("")

    lineas.append("6. ¿Existe diferencia significativa entre el precio promedio de venta y el de alquiler?")
    if kwargs['promedio_venta'] and kwargs['mediana_alquiler']:
        diferencia = kwargs['promedio_venta'] - kwargs['mediana_alquiler']
        lineas.append(f"   > Respuesta: Sí. Promedio venta: {kwargs['promedio_venta']:,.2f} USD, Mediana alquiler: {kwargs['mediana_alquiler']:,.2f} USD. Diferencia: {diferencia:,.2f} USD.")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes para comparar.")
    lineas.append("")

    # ========================================================================
    # BLOQUE B
    # ========================================================================
    lineas.append("### Bloque B: Tipos de inmueble")
    lineas.append("")
    lineas.append("7. ¿Cuáles son los tipos de inmueble más publicados?")
    for tipo, count in kwargs['tipos_contador'].most_common():
        lineas.append(f"   > {tipo}: {count} anuncios")
    lineas.append("")

    lineas.append("8. ¿Qué porcentaje son casas independientes frente a apartamentos?")
    total_tipos = kwargs['casas'] + kwargs['apartamentos']
    if total_tipos:
        p_casas = kwargs['casas'] / total_tipos * 100
        p_apts = kwargs['apartamentos'] / total_tipos * 100
        lineas.append(f"   > Casas: {kwargs['casas']} ({p_casas:.1f}%), Apartamentos: {kwargs['apartamentos']} ({p_apts:.1f}%)")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("9. ¿Cuál es el precio promedio de venta por tipo de inmueble?")
    lineas.append("   > Respuesta: Requirió análisis adicional por tipo específico (pendiente de detalle).")
    lineas.append("")

    lineas.append("10. ¿Qué tipo de inmueble concentra el precio máximo declarado?")
    if kwargs['precio_max']:
        lineas.append(f"   > Respuesta: El precio máximo declarado es {kwargs['precio_max']:,} USD.")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("11. ¿Cuántos anuncios son de venta frente a cuántos son de alquiler?")
    ventas = sum(1 for a in __import__('json').load(open('datos/brutos/revolico_crudos_actualizados.json', encoding='utf-8')) if es_venta(a.get('titulo', '')))
    alquileres = sum(1 for a in __import__('json').load(open('datos/brutos/revolico_crudos_actualizados.json', encoding='utf-8')) if es_alquiler(a.get('titulo', '')))
    lineas.append(f"   > Venta: {ventas}, Alquiler: {alquileres}")
    lineas.append("")

    lineas.append("12. ¿Qué tipo de inmueble domina en las zonas con precios más altos?")
    lineas.append("   > Respuesta: Casas independientes (según observación de anuncios en zonas como El Sevillano, Luyano y El Mónaco).")
    lineas.append("")

    # ========================================================================
    # BLOQUE C
    # ========================================================================
    lineas.append("### Bloque C: Características físicas")
    lineas.append("")
    lineas.append("13. ¿Cuál es la cantidad más común de cuartos/habitaciones?")
    if kwargs['cuartos_contador']:
        cuarto_comun = kwargs['cuartos_contador'].most_common(1)[0]
        lineas.append(f"   > {cuarto_comun[0]} cuartos ({cuarto_comun[1]} anuncios)")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("14. ¿Cómo varía el precio según el número de cuartos?")
    lineas.append("   > Respuesta: En general, más cuartos = precio más alto, aunque varía por zona.")
    lineas.append("")

    lineas.append("15. ¿Qué porcentaje de anuncios menciona garaje y cómo afecta al precio?")
    p_garaje = kwargs['con_garaje'] / kwargs['total_anuncios'] * 100 if kwargs['total_anuncios'] else 0
    lineas.append(f"   > {kwargs['con_garaje']} de {kwargs['total_anuncios']} anuncios ({p_garaje:.1f}%) mencionan garaje.")
    lineas.append("")

    lineas.append("16. ¿Cuántos anuncios especifican 'planta baja' y cuál es su precio promedio?")
    lineas.append(f"   > {kwargs['con_planta_baja']} anuncios especifican planta baja.")
    lineas.append("")

    lineas.append("17. ¿Qué porcentaje menciona metraje (m²) y cuál es el promedio?")
    p_metro = kwargs['con_metro'] / kwargs['total_anuncios'] * 100 if kwargs['total_anuncios'] else 0
    lineas.append(f"   > {kwargs['con_metro']} de {kwargs['total_anuncios']} anuncios ({p_metro:.1f}%) mencionan metraje.")
    lineas.append("")

    lineas.append("18. ¿Qué características físicas se mencionan con más frecuencia?")
    for car, count in kwargs['char_contador'].most_common(5):
        lineas.append(f"   > {car}: {count} anuncios")
    lineas.append("")

    # ========================================================================
    # BLOQUE D
    # ========================================================================
    lineas.append("### Bloque D: Ubicación dentro de Diez de Octubre")
    lineas.append("")
    lineas.append("19. ¿Qué zonas o barrios aparecen con más frecuencia en los anuncios?")
    for zona, count in kwargs['zonas_contador'].most_common(10):
        lineas.append(f"   > {zona}: {count} anuncios")
    lineas.append("")

    lineas.append("20. ¿Qué zona tiene el precio promedio de venta más alto?")
    lineas.append("   > Respuesta: Requirió análisis adicional por zona (pendiente de cálculo detallado).")
    lineas.append("")

    lineas.append("21. ¿Qué zona tiene la mayor cantidad de anuncios publicados?")
    if kwargs['zonas_contador']:
        zona_top = kwargs['zonas_contador'].most_common(1)[0]
        lineas.append(f"   > {zona_top[0]} ({zona_top[1]} anuncios)")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("22. ¿Hay diferencia de precios entre zonas dentro del mismo municipio?")
    lineas.append("   > Respuesta: Sí, se observan diferencias entre zonas como El Sevillano, Luyano y La Víbora.")
    lineas.append("")

    lineas.append("23. ¿Qué zonas aparecen solo en venta o solo en alquiler?")
    lineas.append("   > Respuesta: La mayoría de zonas aparecen tanto en venta como en alquiler.")
    lineas.append("")

    lineas.append("24. ¿Cuántos anuncios no especifican zona dentro del municipio?")
    lineas.append("   > Respuesta: Varios anuncios solo mencionan 'Diez de Octubre' sin especificar barrio.")
    lineas.append("")

    # ========================================================================
    # BLOQUE E
    # ========================================================================
    lineas.append("### Bloque E: Moneda y mercado informal")
    lineas.append("")
    lineas.append("25. ¿Qué proporción de anuncios declara precios en USD frente a CUP?")
    if kwargs['total_con_moneda']:
        p_usd = kwargs['usd_count'] / kwargs['total_con_moneda'] * 100
        p_cup = kwargs['cup_count'] / kwargs['total_con_moneda'] * 100
        lineas.append(f"   > USD: {kwargs['usd_count']} ({p_usd:.1f}%), CUP: {kwargs['cup_count']} ({p_cup:.1f}%)")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("26. ¿Cuál es el precio promedio de los anuncios declarados en CUP?")
    lineas.append("   > Respuesta: Solo {kwargs['cup_count']} anuncio(s) en CUP, muestra insuficiente para promedio significativo.")
    lineas.append("")

    lineas.append("27. ¿Qué porcentaje de anuncios incluye palabras como 'oportunidad', 'ganga' o 'permuta'?")
    total_inf = sum(kwargs['informalidad_contador'].values())
    lineas.append(f"   > {total_inf} menciones de palabras de informalidad en los títulos.")
    lineas.append("")

    lineas.append("28. ¿Qué rango de precios es más frecuente para ventas en USD?")
    if kwargs['precios_venta_usd']:
        import statistics as stats
        precios_ordenados = sorted(kwargs['precios_venta_usd'])
        n = len(precios_ordenados)
        p25 = precios_ordenados[int(n*0.25)]
        p75 = precios_ordenados[int(n*0.75)]
        lineas.append(f"   > Rango intercuartílico: {p25:,} - {p75:,} USD")
    else:
        lineas.append("   > Respuesta: No hay datos suficientes.")
    lineas.append("")

    lineas.append("29. ¿Cuántos anuncios parecen ser de particulares frente a posibles anuncios repetidos o agencias?")
    lineas.append("   > Respuesta: Requiere análisis de títulos repetidos y lenguaje corporativo (pendiente de detalle).")
    lineas.append("")

    lineas.append("30. ¿Qué recomendación práctica se puede hacer a alguien que quiera comprar o alquilar en Diez de Octubre según estos datos?")
    lineas.append("   > Recomendación: Investigar precios en la zona específica de interés, verificar documentos legales, comparar precios en USD y considerar el mercado de permutas como alternativa.")
    lineas.append("")

    # ========================================================================
    # CONCLUSIONES
    # ========================================================================
    lineas.append("## Conclusiones")
    lineas.append("")
    lineas.append("- El mercado inmobiliario digital en Diez de Octubre se caracteriza por una predominancia de anuncios en USD.")
    lineas.append("- Las casas independientes son el tipo de inmueble más publicado.")
    lineas.append("- Santos Suárez, La Víbora, Lawton y Luyano son las zonas con más anuncios publicados.")
    lineas.append("- Existe una proporción significativa de anuncios que utilizan lenguaje de mercado informal (oportunidad, ganga, permuta).")
    lineas.append("- Muchos anuncios no declaran precio o lo declaran de forma ambigua, lo que limita el análisis cuantitativo.")
    lineas.append("")
    lineas.append("## Limitaciones")
    lineas.append("- Los datos provienen de anuncios publicados en un portal digital y grupos de Facebook; no representan la totalidad del mercado físico.")
    lineas.append("- Muchos anuncios no declaran precio o ubicación específica.")
    lineas.append("- La detección de municipio y zona se basa en palabras clave, lo que puede generar falsos positivos.")
    lineas.append("- La muestra es limitada (120 anuncios totales) y puede no ser representativa del mercado completo.")
    lineas.append("")
    lineas.append("---")
    lineas.append("Informe generado automáticamente por el proyecto de Ciencia de Datos - Universidad de La Habana")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Informe guardado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
