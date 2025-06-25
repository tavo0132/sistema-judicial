from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from django.conf import settings
from clientes.models import Radicacion, Cliente
from scraping.models import ResultadoScraping
from django.utils import timezone
import os

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

def log_scraping(mensaje):
    log_dir = r"C:\Users\Gustavo\Documents\Dev\Lenguajes\Python\Fullstack\sistema-judicial-master\scraping\logs_scraper_colombia"
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now()
    log_filename = f"scraping_log_{now.strftime('%d-%m-%Y_%H.%M')}.txt"
    log_path = os.path.join(log_dir, log_filename)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")

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

def consultar_radicaciones(radicados, id_cliente):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        for numero_radicado in radicados:
            datos = scrape_proceso(driver, numero_radicado)
            log_scraping(f"Datos extraídos para {numero_radicado}: {datos}")
            try:
                rad = Radicacion.objects.get(numero_radicado=numero_radicado)
                from datetime import datetime
                if datos["fecha_radicado"]:
                    try:
                        fecha = datetime.strptime(datos["fecha_radicado"], "%Y-%m-%d")
                        rad.fecha_radicado = timezone.make_aware(fecha)
                    except Exception as e:
                        rad.fecha_radicado = None
                        log_scraping(f"Error fecha_radicado: {e}")
                if datos["fecha_ultima_actuacion"]:
                    try:
                        fecha = datetime.strptime(datos["fecha_ultima_actuacion"], "%Y-%m-%d")
                        rad.fecha_ultima_actuacion = timezone.make_aware(fecha)
                    except Exception as e:
                        rad.fecha_ultima_actuacion = None
                        log_scraping(f"Error fecha_ultima_actuacion: {e}")
                if datos["despacho_departamento"]:
                    rad.despacho_departamento = datos["despacho_departamento"]
                if datos["sujetos_procesales"]:
                    rad.sujetos_procesales = datos["sujetos_procesales"]
                log_scraping(f"Antes de guardar: {rad.numero_radicado}, {rad.fecha_radicado}, {rad.fecha_ultima_actuacion}, {rad.despacho_departamento}, {rad.sujetos_procesales}")
                rad.save()
                rad.refresh_from_db()
                log_scraping(f"Verificación en DB: {rad.numero_radicado}, {rad.despacho_departamento}, {rad.sujetos_procesales}")
                log_scraping(f"Después de guardar: {rad.numero_radicado}, {rad.despacho_departamento}, {rad.sujetos_procesales}")
                log_scraping(f"Radicación actualizada: {rad.numero_radicado}")
            except Radicacion.DoesNotExist:
                try:
                    cliente = Cliente.objects.get(id=id_cliente)
                except Cliente.DoesNotExist:
                    log_scraping(f"El cliente con id={id_cliente} no existe, no se puede guardar la radicación {numero_radicado}.")
                    continue

                rad = Radicacion(
                    cliente=cliente,
                    numero_radicado=numero_radicado,
                    fecha_radicado=timezone.now(),
                    fecha_ultima_actuacion=None,
                    proceso_consultado='No',
                    estado_radicado='Abierto',
                    despacho_departamento=datos.get("despacho_departamento"),
                    sujetos_procesales=datos.get("sujetos_procesales"),
                )
                rad.save()
                log_scraping(f"Radicación {numero_radicado} creada para el cliente {cliente.id}")
            time.sleep(3)
    finally:
        driver.quit()