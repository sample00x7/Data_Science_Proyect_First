#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mezcla datos de Facebook y Revolico en un solo JSON.
Los datos de Revolico se convierten a la misma estructura anidada que Facebook.

Lee:
  - datos/brutos/revolico_crudos_actualizados.json (Revolico)
  - /home/luis/Downloads/deepseek_json_20261031_36cb21.json (Facebook)

Escribe:
  - datos/limpios/datos_unificados_facebook_revolico.json
"""

import json
import re
from datetime import datetime

REVOLICO_FILE = "datos/brutos/revolico_crudos_actualizados.json"
FACEBOOK_FILE = "/home/luis/Downloads/deepseek_json_20261031_36cb21.json"
OUTPUT_FILE = "datos/limpios/datos_unificados_facebook_revolico.json"


def extraer_tipo_inmueble(titulo):
    """Intenta extraer el tipo de inmueble del título."""
    titulo_lower = titulo.lower()
    if any(p in titulo_lower for p in ["apartamento", "apto", "apt "]):
        return "Apartamento"
    if any(p in titulo_lower for p in ["casa ", " casa", "casa independiente", "biplanta", "planta baja"]):
        return "Casa"
    if any(p in titulo_lower for p in ["local", "local comercial"]):
        return "Local"
    if any(p in titulo_lower for p in ["terreno", "solar"]):
        return "Terreno"
    if any(p in titulo_lower for p in ["cuarto", "habitacion", "habitación"]):
        return "Cuarto"
    return "Inmueble"


def convertir_revolico_a_estructura_facebook(anuncio, id_global):
    """Convierte un anuncio de Revolico a la estructura anidada de Facebook."""
    titulo = anuncio.get("titulo", "")
    precio = anuncio.get("precio")
    moneda = anuncio.get("moneda", "")
    municipio = anuncio.get("municipio", "")
    enlace = anuncio.get("enlace", "")
    permuta = anuncio.get("permuta", False)
    fecha_agregado = anuncio.get("fecha_agregado", "")
    fecha_verificacion = anuncio.get("fecha_verificacion", "")
    id_anuncio = anuncio.get("id_anuncio", id_global)

    # Determinar tipo de inmueble
    tipo = extraer_tipo_inmueble(titulo)

    # Construir ubicación: municipio + parte del título
    ubicacion = f"{municipio}, {titulo[:80]}" if len(titulo) > 80 else f"{municipio}, {titulo}"

    # Construir estructura tipo Facebook
    anuncio_facebook = {
        "id_publicacion": id_anuncio if id_anuncio else id_global,
        "publicacion": {
            "grupo": "Revolico",
            "autor": "Revolico",
            "fecha": fecha_agregado if fecha_agregado else fecha_verificacion
        },
        "detalles_propiedad": {
            "tipo": tipo,
            "ubicacion": ubicacion,
            "distribucion": []
        },
        "servicios_y_caracteristicas": [],
        "equipamiento_incluido": [],
        "precio": {
            "monto": precio,
            "moneda": moneda,
            "negociable": False,
            "nota": "Permuta: SÍ" if permuta else "Precio fijo"
        },
        "contacto": {
            "telefono": "",
            "metodo": "Vía Revolico",
            "enlace_revolico": enlace
        },
        "fuente": "revolico",
        "estado": anuncio.get("estado", ""),
        "motivo_estado": anuncio.get("motivo_estado", ""),
        "fecha_verificacion": fecha_verificacion
    }

    return anuncio_facebook


def main():
    # Cargar Revolico
    with open(REVOLICO_FILE, encoding="utf-8") as f:
        anuncios_revolico = json.load(f)

    # Cargar Facebook
    with open(FACEBOOK_FILE, encoding="utf-8") as f:
        anuncios_facebook = json.load(f)

    print(f"Revolico: {len(anuncios_revolico)} anuncios")
    print(f"Facebook: {len(anuncios_facebook)} anuncios")

    # Convertir Revolico a estructura de Facebook
    anuncios_revolico_convertidos = []
    for i, anuncio in enumerate(anuncios_revolico, start=1):
        convertido = convertir_revolico_a_estructura_facebook(anuncio, i)
        anuncios_revolico_convertidos.append(convertido)

    # Combinar ambos: Facebook primero, luego Revolico
    datos_unificados = anuncios_facebook + anuncios_revolico_convertidos

    # Guardar
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(datos_unificados, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"RESULTADO")
    print(f"{'=' * 60}")
    print(f"Facebook:  {len(anuncios_facebook)} anuncios")
    print(f"Revolico:  {len(anuncios_revolico_convertidos)} anuncios (convertidos a estructura Facebook)")
    print(f"Total:     {len(datos_unificados)} anuncios")
    print(f"Archivo:   {OUTPUT_FILE}")

    # Mostrar ejemplo del primer anuncio de cada fuente
    print(f"\nEjemplo Facebook (id_publicacion={datos_unificados[0]['id_publicacion']}):")
    print(json.dumps(datos_unificados[0], ensure_ascii=False, indent=2)[:500])

    idx_fb = len(anuncios_facebook)
    print(f"\nEjemplo Revolico (id_publicacion={datos_unificados[idx_fb]['id_publicacion']}):")
    print(json.dumps(datos_unificados[idx_fb], ensure_ascii=False, indent=2)[:500])


if __name__ == "__main__":
    main()
