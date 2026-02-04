import requests
import json
import os
from datetime import datetime

# CONFIGURACIÓN
URL_OBJETIVO = "https://programamos.es/"
API_KEY = os.environ.get("PAGESPEED_API_KEY") 

def obtener_metricas(estrategia):
    """
    Estrategia puede ser 'mobile' o 'desktop'
    NOTA: Para obtener SEO y Accesibilidad, hay que pedirlo explícitamente en la URL
    con el parámetro 'category'.
    """
    base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    # Pedimos explícitamente performance, seo y accessibility
    params = f"?url={URL_OBJETIVO}&strategy={estrategia}&category=performance&category=seo&category=accessibility&key={API_KEY}"
    url_api = base_url + params
    
    response = requests.get(url_api)
    
    if response.status_code != 200:
        print(f"Error en la API ({estrategia}): {response.text}")
        return None

    return response.json()

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    print(f"[{timestamp}] Iniciando auditoría completa para {URL_OBJETIVO}...")
    
    # 1. Obtener datos
    datos_mobile = obtener_metricas("mobile")
    datos_desktop = obtener_metricas("desktop")
    
    if not datos_mobile or not datos_desktop:
        print("Falló la obtención de datos. Abortando.")
        return

    # 2. Extraer métricas (Ahora incluimos accesibilidad que pide la guía)
    try:
        resultado_final = {
            "fecha": timestamp,
            "url": URL_OBJETIVO,
            "mobile": {
                "performance": datos_mobile["lighthouseResult"]["categories"]["performance"]["score"] * 100, # Escala 0-100
                "seo": datos_mobile["lighthouseResult"]["categories"]["seo"]["score"] * 100,
                "accessibility": datos_mobile["lighthouseResult"]["categories"]["accessibility"]["score"] * 100,
                "lcp": datos_mobile["lighthouseResult"]["audits"]["largest-contentful-paint"]["displayValue"],
                "tbt": datos_mobile["lighthouseResult"]["audits"]["total-blocking-time"]["displayValue"]
            },
            "desktop": {
                "performance": datos_desktop["lighthouseResult"]["categories"]["performance"]["score"] * 100,
                "seo": datos_desktop["lighthouseResult"]["categories"]["seo"]["score"] * 100,
                "accessibility": datos_desktop["lighthouseResult"]["categories"]["accessibility"]["score"] * 100
            }
        }

        # 3. Guardar en carpeta 'data/seo'
        # Aseguramos que la ruta sea relativa al root del repo o absoluta
        output_dir = "data/seo"
        os.makedirs(output_dir, exist_ok=True)
        nombre_archivo = f"{output_dir}/metrics_{timestamp}.json"
        
        with open(nombre_archivo, "w") as f:
            json.dump(resultado_final, f, indent=4)
        
        print(f"¡Éxito! Datos guardados en {nombre_archivo}")

    except KeyError as e:
        print(f"Error procesando el JSON: Falta la clave {e}")
        # Imprimir las claves disponibles para debug
        print("Claves disponibles en categories:", datos_mobile["lighthouseResult"]["categories"].keys())

if __name__ == "__main__":
    main()