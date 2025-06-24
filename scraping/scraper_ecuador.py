from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from django.conf import settings
from clientes.models import Radicacion
from .models import ResultadoScraping

def scrape_proceso(driver, radicacion):
    try:
        # Configurar tiempo de espera explícito
        wait = WebDriverWait(driver, 20)
        
        # Cargar la página
        driver.get("https://procesosjudiciales.funcionjudicial.gob.ec/busqueda")
        
        # Esperar y ubicar el campo de entrada
        input_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )
        
        # Limpiar el campo y escribir la radicación
        input_field.clear()
        time.sleep(1)  # Pequeña pausa para estabilidad
        input_field.send_keys(radicacion)
        
        # Esperar y hacer clic en "Todas las instancias"
        all_processes = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.v-radio:nth-child(2)"))
        )
        driver.execute_script("arguments[0].click();", all_processes)
        
        # Enviar el formulario
        input_field.send_keys(Keys.RETURN)
        
        # Esperar a que aparezca la tabla
        tabla = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
        )
        
        # Procesar las fechas
        texto_completo = tabla.text
        lineas = texto_completo.split('\n')
        
        for linea in lineas:
            if linea.strip().startswith('20') and len(linea.strip()) >= 10:
                fecha_str = linea.strip()[:10]  # Tomar solo los primeros 10 caracteres (YYYY-MM-DD)
                try:
                    fecha_actual = datetime.now()
                    fecha_actuacion = datetime.strptime(fecha_str, "%Y-%m-%d")
                    
                    if (fecha_actual - fecha_actuacion).days < 365:
                        # Guardar en la base de datos
                        ResultadoScraping.objects.create(
                            radicacion=radicacion,
                            fecha_actuacion=fecha_actuacion,
                            descripcion=linea.strip()
                        )
                except ValueError:
                    continue
                
    except Exception as e:
        print(f"Error procesando {radicacion}: {str(e)}")
        
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