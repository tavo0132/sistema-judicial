import os
import sys

# Agrega la ruta raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import django
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from notifications.notifications_colombia import obtener_fecha_actuacion_reciente

# Configura el entorno de Django para acceder a los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

from clientes.models import Radicacion

def scrape_proceso(driver, numero_radicado):
    wait = WebDriverWait(driver, 20)
    resultado = {
        "numero_radicado": numero_radicado,
        "fecha_radicado": None,
        "fecha_ultima_actuacion": None,
        "despacho_departamento": None,
        "sujetos_procesales": None,
    }
    try:
        driver.get("https://consultaprocesos.ramajudicial.gov.co/Procesos/NumeroRadicacion")
        input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        input_field.clear()
        time.sleep(1)
        input_field.send_keys(numero_radicado)
        all_processes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.v-radio:nth-child(2)")))
        driver.execute_script("arguments[0].click();", all_processes)
        input_field.send_keys(Keys.RETURN)
        tabla = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody")))
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        if filas and len(filas) >= 1:
            celdas = filas[0].find_elements(By.TAG_NAME, "td")
            if len(celdas) >= 5:
                fechas = celdas[2].text.strip().split('\n')
                if len(fechas) >= 2:
                    resultado["fecha_radicado"] = fechas[0]
                    resultado["fecha_ultima_actuacion"] = fechas[1]
                resultado["despacho_departamento"] = celdas[3].text.strip()
                resultado["sujetos_procesales"] = celdas[4].text.strip().replace('\n', ' | ')
        print(tabla.text)
        # Aquí se integra la función de notificación
        obtener_fecha_actuacion_reciente(tabla.text)
    except Exception as e:
        print(f"Error procesando {numero_radicado}: {str(e)}")
    return resultado

def log_scraping(mensaje):
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs_scraper_colombia")
    os.makedirs(log_dir, exist_ok=True)
    now = time.strftime("%d-%m-%Y_%H.%M")
    log_filename = f"scraping_log_{now}.txt"
    log_path = os.path.join(log_dir, log_filename)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")

def main():
    # Obtiene todos los números de radicado desde la base de datos
    radicados = list(Radicacion.objects.values_list('numero_radicado', flat=True))
    resultados = []

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    try:
        for numero_radicado in radicados:
            datos = scrape_proceso(driver, numero_radicado)
            resultados.append(datos)
            log_scraping(f"Datos extraídos para {numero_radicado}: {datos}")
            time.sleep(3)
    finally:
        driver.quit()

    # Guardar resultados en un archivo JSON en la carpeta scraping
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "resultados_scraping.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    print(f"\nResultados guardados en {output_path}")

if __name__ == "__main__":
    main()