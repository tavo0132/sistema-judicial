from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from django.conf import settings
from clientes.models import Radicacion
from scraping.models import ResultadoScraping
from django.utils import timezone

def scrape_proceso(driver, numero_radicado):
    wait = WebDriverWait(driver, 20)
    resultado = {
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
        # Esperar a que aparezca la tabla de resultados
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
        return resultado
    except Exception as e:
        print(f"Error procesando {numero_radicado}: {str(e)}")
        return resultado

def actualizar_radicaciones():
    # Obtener todas las radicaciones de la base de datos
    radicaciones = Radicacion.objects.all()
    
    # Configurar opciones de Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Iniciar el navegador
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    try:
        for radicacion in radicaciones:
            scrape_proceso(driver, radicacion.numero_radicado)
            time.sleep(3)  # Pausa entre consultas
    finally:
        driver.quit()

def consultar_radicaciones(radicados):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        for numero_radicado in radicados:
            datos = scrape_proceso(driver, numero_radicado)
            print(f"Datos extraídos para {numero_radicado}: {datos}")  # <-- Agrega esto
            try:
                rad = Radicacion.objects.get(numero_radicado=numero_radicado)
                from datetime import datetime
                if datos["fecha_radicado"]:
                    try:
                        fecha = datetime.strptime(datos["fecha_radicado"], "%Y-%m-%d")
                        rad.fecha_radicado = timezone.make_aware(fecha)
                    except Exception:
                        rad.fecha_radicado = None
                if datos["fecha_ultima_actuacion"]:
                    try:
                        fecha = datetime.strptime(datos["fecha_ultima_actuacion"], "%Y-%m-%d")
                        rad.fecha_ultima_actuacion = timezone.make_aware(fecha)
                    except Exception:
                        rad.fecha_ultima_actuacion = None
                if datos["despacho_departamento"]:
                    print("Asignando despacho_departamento:", datos["despacho_departamento"])
                    rad.despacho_departamento = datos["despacho_departamento"]
                if datos["sujetos_procesales"]:
                    print("Asignando sujetos_procesales:", datos["sujetos_procesales"])
                    rad.sujetos_procesales = datos["sujetos_procesales"]
                print("Antes de guardar:", rad.fecha_radicado, rad.fecha_ultima_actuacion, rad.despacho_departamento, rad.sujetos_procesales)
                rad.save()
            except Radicacion.DoesNotExist:
                print(f"Radicación {numero_radicado} no encontrada en la base de datos.")
            time.sleep(3)
    finally:
        driver.quit()