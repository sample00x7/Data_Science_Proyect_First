#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica anuncios activos y agrega nuevos del municipio Diez de Octubre.
VERSION OPTIMIZADA: progreso parcial cada 10, sleep corto, manejo de errores.

Lee:  datos/brutos/revolico_crudos.json
Escribe: datos/brutos/revolico_crudos_actualizados.json
Escribe: datos/limpios/anuncios_activos.txt
Escribe: datos/limpios/anuncios_inactivos.txt
Escribe: datos/limpios/nuevos_anuncios.txt
Escribe: datos/limpios/reporte_actualizacion_anuncios.txt
"""

import json
import re
import time
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

INPUT_FILE = "datos/brutos/revolico_crudos.json"
OUTPUT_FILE = "datos/brutos/revolico_crudos_actualizados.json"
REPORT_FILE = "datos/limpios/reporte_actualizacion_anuncios.txt"
ACTIVOS_FILE = "datos/limpios/anuncios_activos.txt"
INACTIVOS_FILE = "datos/limpios/anuncios_inactivos.txt"
NUEVOS_FILE = "datos/limpios/nuevos_anuncios.txt"
PROGRESS_FILE = "datos/brutos/revolico_progreso_actualizacion.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

ZONAS_DIEZ_DE_OCTUBRE = [
    "diez de octubre", "10 de octubre", "santos suarez", "santos suárez",
    "la vibora", "la víbora", "lawton", "luyano", "el sevillano", "sevillano",
    "monaco", "mónaco", "asuncion", "asunción", "santa catalina", "vista alegre",
    "reparto asuncion", "reparto lawton", "reparto sevillano", "vía blanca",
    "via blanca", "calzada 10 de octubre", "calzada diez de octubre",
    "diez de octubre y", "10 de octubre y",
]


def es_de_diez_de_octubre(titulo, enlace):
    texto = (titulo + " " + enlace).lower()
    for zona in ZONAS_DIEZ_DE_OCTUBRE:
        if zona in texto:
            return True
    return False

URL_BUSQUEDA = (
    "https://www.revolico.com/search"
    "?category=inmobiliaria&province=la-habana&municipio=diez-de-octubre"
)

ID_PATTERN = re.compile(r"-(\d{7,10})\??$")


def extraer_id_desde_enlace(enlace):
    if not enlace:
        return None
    m = re.search(r"-(\d{7,10})\??$", enlace)
    if m:
        return int(m.group(1))
    m = re.search(r"/(\d{7,10})/?$", enlace)
    if m:
        return int(m.group(1))
    return None


def es_anuncio_valido(titulo, enlace):
    if not titulo or not enlace:
        return False
    titulo_lower = titulo.lower().strip()
    if "publicar anuncio" in titulo_lower:
        return False
    if "/item/publish" in enlace:
        return False
    if re.fullmatch(r"[\d.,\s\$€£¥usdcup]+", titulo_lower) and len(titulo_lower) <= 12:
        return False
    return True


def verificar_anuncio_activo(enlace):
    """Devuelve (activo: bool, motivo: str). Cualquier error = inactivo."""
    try:
        resp = requests.get(enlace, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            texto = resp.text.lower()
            indicadores_inactivo = [
                "anuncio no disponible",
                "anuncio eliminado",
                "este anuncio ya no",
                "página no encontrada",
                "404",
                "anuncio caducado",
                "no se encontró el anuncio",
            ]
            for ind in indicadores_inactivo:
                if ind in texto:
                    return False, "Anuncio eliminado o no disponible"
            return True, "Activo"
        elif resp.status_code == 404:
            return False, "Error 404 - Página no encontrada"
        elif resp.status_code == 403:
            return False, "Error 403 - Acceso denegado"
        else:
            return False, f"Error HTTP {resp.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout de conexión"
    except requests.exceptions.ConnectionError:
        return False, "Error de conexión"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"


def guardar_progreso(anuncios_activos, anuncios_inactivos, indice_actual, total, anuncios_nuevos):
    datos = {
        "anuncios_activos": anuncios_activos,
        "anuncios_inactivos": anuncios_inactivos,
        "anuncios_nuevos": anuncios_nuevos,
        "indice_procesado": indice_actual,
        "total": total,
        "fecha_guardado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def cargar_progreso():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    from datetime import datetime

    print("=" * 80)
    print("VERIFICACIÓN Y ACTUALIZACIÓN DE ANUNCIOS - DIEZ DE OCTUBRE")
    print("=" * 80)

    # Cargar anuncios existentes
    print("\n[1/4] Cargando anuncios existentes...")
    with open(INPUT_FILE, encoding="utf-8") as f:
        anuncios_existentes = json.load(f)
    print(f"  Total: {len(anuncios_existentes)}")

    # Verificar progreso previo
    prev = cargar_progreso()
    if prev:
        anuncios_activos = prev["anuncios_activos"]
        anuncios_inactivos = prev["anuncios_inactivos"]
        anuncios_nuevos = prev.get("anuncios_nuevos", [])
        indice_inicio = prev["indice_procesado"]
        print(f"  Reanudando desde anuncio {indice_inicio + 1}")
    else:
        anuncios_activos = []
        anuncios_inactivos = []
        anuncios_nuevos = []
        indice_inicio = 0

    # Verificar anuncios existentes
    print("\n[2/4] Verificando anuncios activos...")
    total = len(anuncios_existentes)

    for i in range(indice_inicio, total):
        anuncio = anuncios_existentes[i]
        enlace = anuncio.get("enlace", "")
        titulo = anuncio.get("titulo", "")

        print(f"  [{i + 1:3d}/{total}] {titulo[:55]}...", end=" ")

        activo, motivo = verificar_anuncio_activo(enlace)

        anuncio_copia = dict(anuncio)
        anuncio_copia["estado"] = "activo" if activo else "inactivo"
        anuncio_copia["motivo_estado"] = motivo
        anuncio_copia["fecha_verificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if activo:
            anuncios_activos.append(anuncio_copia)
            print("ACTIVO")
        else:
            anuncios_inactivos.append(anuncio_copia)
            print(f"INACTIVO - {motivo}")

        # Guardar progreso cada 10
        if (i + 1) % 10 == 0:
            guardar_progreso(anuncios_activos, anuncios_inactivos, i + 1, total, anuncios_nuevos)
            print(f"    >> Progreso guardado ({i + 1}/{total})")

        time.sleep(0.3)

    # Buscar nuevos anuncios
    print("\n[3/4] Buscando nuevos anuncios en Revolico (Diez de Octubre)...")
    ids_existentes = set()
    for a in anuncios_activos:
        id_a = extraer_id_desde_enlace(a.get("enlace", ""))
        if id_a:
            ids_existentes.add(id_a)

    for pagina in range(1, 4):  # 3 páginas
        url_pagina = f"{URL_BUSQUEDA}&page={pagina}" if pagina > 1 else URL_BUSQUEDA
        print(f"  Página {pagina}...")
        try:
            resp = requests.get(url_pagina, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                count = 0
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"]
                    texto = a_tag.get_text(" ", strip=True)
                    if not es_anuncio_valido(texto, href):
                        continue
                    if "/item/" not in href:
                        continue
                    from urllib.parse import urljoin
                    enlace_abs = urljoin(url_pagina, href)
                    id_a = extraer_id_desde_enlace(enlace_abs)
                    if not id_a or id_a in ids_existentes:
                        continue
                    if not es_de_diez_de_octubre(texto, enlace_abs):
                        continue
                    # Extraer precio del texto del padre
                    precio = None
                    moneda = ""
                    padre = a_tag.parent
                    if padre:
                        texto_padre = padre.get_text(" ", strip=True)
                        m = re.search(r"([\d.,]+)\s*(USD|CUP|\$)", texto_padre)
                        if m:
                            try:
                                precio = int(m.group(1).replace(",", "").replace(".", ""))
                            except ValueError:
                                precio = None
                            moneda = m.group(2)
                            if moneda == "$":
                                moneda = "USD"
                    anuncios_nuevos.append({
                        "titulo": texto,
                        "precio": precio,
                        "moneda": moneda,
                        "municipio": "Diez de Octubre",
                        "enlace": enlace_abs,
                        "permuta": "permuta" in texto.lower() or "intercambio" in texto.lower(),
                        "id_anuncio": id_a,
                        "fuente": "nuevo_scraping",
                        "fecha_agregado": datetime.now().strftime("%Y-%m-%d"),
                        "estado": "activo",
                        "motivo_estado": "Nuevo anuncio",
                        "fecha_verificacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    ids_existentes.add(id_a)
                    count += 1
                    print(f"    NUEVO: {texto[:50]}... ({precio} {moneda})")
                print(f"    Página {pagina}: {count} nuevos")
            else:
                print(f"    Error HTTP {resp.status_code}")
        except Exception as e:
            print(f"    Error página {pagina}: {str(e)[:50]}")
        time.sleep(1)

    # Unificar
    print("\n[4/4] Guardando resultados...")
    todos = anuncios_activos + anuncios_nuevos
    ids_vistos = set()
    unificados = []
    for a in todos:
        id_a = a.get("id_anuncio") or extraer_id_desde_enlace(a.get("enlace", ""))
        clave = id_a if id_a else a.get("enlace", "")
        if clave and clave not in ids_vistos:
            ids_vistos.add(clave)
            unificados.append(a)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unificados, f, ensure_ascii=False, indent=2)

    with open(ACTIVOS_FILE, "w", encoding="utf-8") as f:
        for a in anuncios_activos:
            f.write(f"{a['precio']} {a['moneda']} | {a['titulo']} | {a['enlace']}\n")

    with open(INACTIVOS_FILE, "w", encoding="utf-8") as f:
        for a in anuncios_inactivos:
            f.write(f"{a['precio']} {a['moneda']} | {a['titulo']} | {a['enlace']} | {a['motivo_estado']}\n")

    with open(NUEVOS_FILE, "w", encoding="utf-8") as f:
        for a in anuncios_nuevos:
            f.write(f"{a['precio']} {a['moneda']} | {a['titulo']} | {a['enlace']}\n")

    # Reporte
    lineas = []
    lineas.append("=" * 80)
    lineas.append("REPORTE DE ACTUALIZACIÓN DE ANUNCIOS - DIEZ DE OCTUBRE")
    lineas.append("=" * 80)
    lineas.append("")
    lineas.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lineas.append("")
    lineas.append(f"Anuncios originales:    {len(anuncios_existentes)}")
    lineas.append(f"Anuncios activos:       {len(anuncios_activos)}")
    lineas.append(f"Anuncios inactivos:     {len(anuncios_inactivos)}")
    lineas.append(f"Nuevos anuncios:        {len(anuncios_nuevos)}")
    lineas.append(f"Total final:            {len(unificados)}")
    lineas.append("")
    lineas.append("ANUNCIOS INACTIVOS:")
    for a in anuncios_inactivos:
        lineas.append(f"  {a['precio']} {a['moneda']} | {a['titulo']} | {a['motivo_estado']}")
    lineas.append("")
    lineas.append("NUEVOS ANUNCIOS:")
    for a in anuncios_nuevos:
        lineas.append(f"  {a['precio']} {a['moneda']} | {a['titulo']}")
    lineas.append("=" * 80)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"\n{'=' * 80}")
    print(f"Total originales: {len(anuncios_existentes)}")
    print(f"Activos: {len(anuncios_activos)}")
    print(f"Inactivos: {len(anuncios_inactivos)}")
    print(f"Nuevos: {len(anuncios_nuevos)}")
    print(f"Total final: {len(unificados)}")
    print("Archivos guardados.")


if __name__ == "__main__":
    main()
