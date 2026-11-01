#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae la fecha de publicación de cada anuncio de Revolico visitando su ficha individual.
VERSION OPTIMIZADA: guardado parcial cada 10 anuncios.

Lee:  datos/brutos/revolico_crudos_actualizados.json
Escribe: datos/brutos/revolico_crudos_con_fechas.json
Escribe: datos/limpios/reporte_limpieza_fechas.txt
"""

import json
import re
import time
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

INPUT_FILE = "datos/brutos/revolico_crudos_actualizados.json"
OUTPUT_FILE = "datos/brutos/revolico_crudos_con_fechas.json"
REPORT_FILE = "datos/limpios/reporte_limpieza_fechas.txt"
PROGRESS_FILE = "datos/brutos/revolico_progreso_fechas.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

FECHA_PATRONES = [
    r"(\d{1,2})/(\d{1,2})/(\d{4})",
    r"(\d{4})-(\d{1,2})-(\d{1,2})",
    r"(\d{1,2})-(\d{1,2})-(\d{4})",
    r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})",
    r"(\d{1,2})\s+de\s+(\w+)\s+(\d{4})",
]

MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def normalizar_fecha(texto):
    if not texto:
        return None
    texto = texto.strip()
    for patron in FECHA_PATRONES:
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            grupos = m.groups()
            if len(grupos) == 3:
                if "de" in patron:
                    try:
                        dia = int(grupos[0])
                        mes_nombre = grupos[1].lower()
                        anio = int(grupos[2])
                        mes = MESES_ES.get(mes_nombre)
                        if mes:
                            return f"{anio:04d}-{mes:02d}-{dia:02d}"
                    except ValueError:
                        continue
                else:
                    try:
                        a = int(grupos[0])
                        b = int(grupos[1])
                        c = int(grupos[2])
                        if c > 31:
                            return f"{c:04d}-{a:02d}-{b:02d}"
                        elif a > 12:
                            return f"{c:04d}-{b:02d}-{a:02d}"
                        else:
                            return f"{c:04d}-{b:02d}-{a:02d}"
                    except ValueError:
                        continue
    return None


session = None

def get_session():
    global session
    if session is None:
        session = requests.Session()
        session.headers.update(HEADERS)
    return session

def extraer_fecha_desde_html(html):
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    for meta in soup.find_all("meta"):
        propiedad = meta.get("property", "") or meta.get("name", "")
        if propiedad in ("article:published_time", "og:published_time", "datePublished"):
            contenido = meta.get("content")
            if contenido:
                fecha = normalizar_fecha(contenido)
                if fecha:
                    return fecha

    time_el = soup.find("time")
    if time_el:
        datetime_attr = time_el.get("datetime")
        if datetime_attr:
            fecha = normalizar_fecha(datetime_attr)
            if fecha:
                return fecha
        texto_time = time_el.get_text(strip=True)
        if texto_time:
            fecha = normalizar_fecha(texto_time)
            if fecha:
                return fecha

    texto = soup.get_text(" ", strip=True)
    for patron in FECHA_PATRONES:
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            fecha = normalizar_fecha(m.group(0))
            if fecha:
                return fecha

    for palabra in ["publicado", "fecha", "publicación", "creado"]:
        idx = texto.lower().find(palabra)
        if idx != -1:
            contexto = texto[idx:idx + 50]
            fecha = normalizar_fecha(contexto)
            if fecha:
                return fecha

    return None


def guardar_progreso(anuncios, indice_actual):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "anuncios": anuncios,
            "indice_procesado": indice_actual,
            "fecha_guardado": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, f, ensure_ascii=False, indent=2)


def cargar_progreso():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            datos = json.load(f)
        return datos["anuncios"], datos["indice_procesado"]
    return None, 0


def main():
    os.makedirs("datos/limpios", exist_ok=True)

    anuncios_previos, indice_inicio = cargar_progreso()
    if anuncios_previos is not None:
        print(f"Reanudando desde anuncio {indice_inicio + 1}")
        anuncios = anuncios_previos
    else:
        with open(INPUT_FILE, encoding="utf-8") as f:
            anuncios = json.load(f)
        indice_inicio = 0

    total = len(anuncios)
    print(f"Total de anuncios: {total}")
    print(f"Comenzando desde el índice: {indice_inicio}")

    con_fecha = sum(1 for a in anuncios if a.get("fecha_publicacion"))
    sin_fecha = sum(1 for a in anuncios if not a.get("fecha_publicacion"))
    errores = 0

    for i in range(indice_inicio, total):
        anuncio = anuncios[i]
        enlace = anuncio.get("enlace", "")

        if anuncio.get("fecha_publicacion"):
            continue

        print(f"[{i + 1:3d}/{total}] {anuncio.get('titulo', 'Sin título')[:55]}...", end=" ")

        try:
            resp = get_session().get(enlace, timeout=10)
            if resp.status_code == 200:
                fecha = extraer_fecha_desde_html(resp.text)
                if fecha:
                    anuncio["fecha_publicacion"] = fecha
                    anuncio["fecha_extraccion"] = datetime.now().strftime("%Y-%m-%d")
                    con_fecha += 1
                    print(f"OK -> {fecha}")
                else:
                    anuncio["fecha_publicacion"] = None
                    anuncio["fecha_extraccion"] = datetime.now().strftime("%Y-%m-%d")
                    sin_fecha += 1
                    print("SIN FECHA")
            else:
                anuncio["fecha_publicacion"] = None
                anuncio["fecha_extraccion"] = datetime.now().strftime("%Y-%m-%d")
                errores += 1
                print(f"HTTP {resp.status_code}")
        except Exception as e:
            anuncio["fecha_publicacion"] = None
            anuncio["fecha_extraccion"] = datetime.now().strftime("%Y-%m-%d")
            errores += 1
            print(f"ERROR: {str(e)[:50]}")

        if (i + 1) % 10 == 0:
            guardar_progreso(anuncios, i + 1)
            print(f"  >> Progreso guardado ({i + 1}/{total})")

        time.sleep(0.1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(anuncios, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Total: {total}")
    print(f"Con fecha: {con_fecha}")
    print(f"Sin fecha: {sin_fecha}")
    print(f"Errores: {errores}")
    print(f"Guardado en: {OUTPUT_FILE}")

    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

    generar_reporte(anuncios, con_fecha, sin_fecha, errores)


def generar_reporte(anuncios, con_fecha, sin_fecha, errores):
    from datetime import datetime, timedelta

    hoy = datetime.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    hace_30_dias = hoy - timedelta(days=30)
    hace_90_dias = hoy - timedelta(days=90)

    recientes = []
    semana = []
    mes = []
    mas_antiguos = []
    sin_fecha_lista = []

    for a in anuncios:
        fecha_str = a.get("fecha_publicacion")
        if not fecha_str:
            sin_fecha_lista.append(a)
            continue
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            sin_fecha_lista.append(a)
            continue

        if fecha >= hace_7_dias:
            recientes.append(a)
        elif fecha >= hace_30_dias:
            semana.append(a)
        elif fecha >= hace_90_dias:
            mes.append(a)
        else:
            mas_antiguos.append(a)

    lineas = []
    lineas.append("=" * 80)
    lineas.append("REPORTE DE LIMPIEZA POR TIEMPO DE PUBLICACIÓN")
    lineas.append("=" * 80)
    lineas.append("")
    lineas.append(f"Fecha del reporte: {hoy.strftime('%d/%m/%Y')}")
    lineas.append(f"Total de anuncios procesados: {len(anuncios)}")
    lineas.append(f"Anuncios con fecha extraída: {con_fecha}")
    lineas.append(f"Anuncios sin fecha: {sin_fecha}")
    lineas.append(f"Errores HTTP: {errores}")
    lineas.append("")
    lineas.append("-" * 80)
    lineas.append("DISTRIBUCIÓN POR ANTIGÜEDAD")
    lineas.append("-" * 80)
    lineas.append("")
    lineas.append(f"Últimos 7 días (muy recientes):     {len(recientes):3d} anuncios")
    lineas.append(f"Entre 8 y 30 días (recientes):      {len(semana):3d} anuncios")
    lineas.append(f"Entre 31 y 90 días (mediante):      {len(mes):3d} anuncios")
    lineas.append(f"Más de 90 días (antiguos):          {len(mas_antiguos):3d} anuncios")
    lineas.append(f"Sin fecha detectada:                {len(sin_fecha_lista):3d} anuncios")
    lineas.append("")
    lineas.append("-" * 80)
    lineas.append("ANUNCIOS RECIENTES (ÚLTIMOS 7 DÍAS)")
    lineas.append("-" * 80)
    for a in recientes:
        lineas.append(f"  [{a['fecha_publicacion']}] {a['titulo'][:70]}")
        lineas.append(f"      Precio: {a['precio']} {a['moneda']} | Municipio: {a['municipio']}")
        lineas.append(f"      Enlace: {a['enlace']}")
        lineas.append("")

    lineas.append("-" * 80)
    lineas.append("ANUNCIOS SIN FECHA DETECTADA")
    lineas.append("-" * 80)
    for a in sin_fecha_lista:
        lineas.append(f"  [{a['precio']} {a['moneda']}] {a['titulo'][:70]}")
        lineas.append(f"      Municipio: {a['municipio']} | Enlace: {a['enlace']}")
        lineas.append("")

    lineas.append("-" * 80)
    lineas.append("ANUNCIOS ANTIGUOS (MÁS DE 90 DÍAS)")
    lineas.append("-" * 80)
    for a in mas_antiguos:
        lineas.append(f"  [{a['fecha_publicacion']}] {a['titulo'][:70]}")
        lineas.append(f"      Precio: {a['precio']} {a['moneda']} | Municipio: {a['municipio']}")
        lineas.append("")

    lineas.append("=" * 80)
    lineas.append("RECOMENDACIONES DE LIMPIEZA POR FECHA")
    lineas.append("=" * 80)
    lineas.append("")
    lineas.append("1. Anuncios con más de 90 días: Pueden ya no estar activos.")
    lineas.append("   Considerar excluirlos del análisis de precios actuales.")
    lineas.append("")
    lineas.append("2. Anuncios sin fecha: No se pudo determinar cuándo se publicaron.")
    lineas.append("   Se recomienda visitar manualmente o excluirlos del análisis temporal.")
    lineas.append("")
    lineas.append("3. Anuncios recientes (últimos 7 días): Los más confiables para")
    lineas.append("   reflejar el precio actual del mercado en 10 de Octubre.")
    lineas.append("")
    lineas.append("4. Para el proyecto de 3 días, priorizar anuncios de los últimos 30 días")
    lineas.append("   para obtener una visión realista del mercado actual.")
    lineas.append("")
    lineas.append("=" * 80)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Reporte guardado en: {REPORT_FILE}")


if __name__ == "__main__":
    main()
