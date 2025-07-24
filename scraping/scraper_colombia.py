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
from notifications.email_sender import EmailSender
from notifications.notifications_colombia import obtener_fecha_actuacion_reciente

# Configura el entorno de Django para acceder a los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

from clientes.models import Radicacion

# Configuración del remitente (puedes moverlo a settings o variables de entorno)
EMAIL = "tavo0132@gmail.com"
PASSWORD = "jbuf phcp ymnp fhjy"  # Reemplaza con tu contraseña de aplicación
sender = EmailSender(EMAIL, PASSWORD)

def scrape_proceso(driver, numero_radicado):
    wait = WebDriverWait(driver, 20)
    resultado = {
        "numero_radicado": numero_radicado,
        "fecha_radicado": None,
        "fecha_ultima_actuacion": None,
        "despacho_departamento": None,
        "sujetos_procesales": None,
    }
    correo_enviado = None
    mensaje_log = ""
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
        # Ejemplo de extracción de demandante y demandado (ajusta según tu lógica real)
        demandante = ""
        demandado = ""
        for linea in tabla.text.split('\n'):
            if linea.startswith("Demandante:"):
                demandante = linea.replace("Demandante:", "").strip()
            if linea.startswith("Demandado:"):
                demandado = linea.replace("Demandado:", "").strip()

        print(tabla.text)
        fecha_reciente = obtener_fecha_actuacion_reciente(tabla.text)
        correos_clientes = []
        correo_enviado = False
        mensaje_log = ""
        
        if fecha_reciente:
            try:
                # Buscar TODAS las radicaciones con este número (puede haber múltiples clientes)
                radicaciones = Radicacion.objects.filter(numero_radicado=numero_radicado)
                for radicacion in radicaciones:
                    correos_clientes.append({
                        'email': radicacion.cliente.email,
                        'nombre': radicacion.cliente.first_name,
                        'cliente_id': radicacion.cliente.id
                    })
            except Exception as e:
                mensaje_log = f"Error obteniendo clientes para radicado {numero_radicado}: {e}"
                print(mensaje_log)
            
            # Enviar correo a TODOS los clientes que tienen este número de radicado
            correo_enviado = False
            for cliente_info in correos_clientes:
                try:
                    asunto = f"Actualización Proceso Judicial - {numero_radicado}"
                    mensaje = f"""
                    <html>
                    <body>
                        <p>Hola, <b>{cliente_info['nombre']}</b></p>
                        <h2 style="color:#1a237e;">Consulta Proceso Judicial</h2>
                        <b>Información del Proceso</b><br>
                        <b>Radicación:</b> {numero_radicado}<br>
                        <b>Despacho:</b> {resultado.get("despacho_departamento", "")}<br>
                        <b>Demandante:</b> {demandante}<br>
                        <b>Demandado:</b> {demandado}<br>
                        <b>Fecha de radicado:</b> {resultado.get("fecha_radicado", "")}<br>
                        <b>Última actuación:</b> {fecha_reciente}<br>
                        <hr>
                        <p style="color:green;"><b>¡Se ha registrado una actuación reciente en su proceso judicial!</b></p>
                        <p>Consulte el sistema para más detalles.</p>
                        <br>
                        <p>Saludos,<br><b>Sistema Judicial</b></p>
                        <small>Este es un mensaje automático, no responda a este correo.</small>
                    </body>
                    </html>
                    """
                    correo_individual = sender.enviar_correo(cliente_info['email'], asunto, mensaje, html=True)
                    if correo_individual:
                        correo_enviado = True
                        print(f"✅ Correo enviado a {cliente_info['email']} ({cliente_info['nombre']})")
                    else:
                        print(f"❌ Fallo al enviar correo a {cliente_info['email']} ({cliente_info['nombre']})")
                except Exception as e:
                    print(f"❌ Error enviando correo a {cliente_info['email']}: {e}")
        else:
            mensaje_log = "No se encontró actuación reciente."
            correo_enviado = False
    except Exception as e:
        mensaje_log = f"Error procesando {numero_radicado}: {str(e)}"
        correo_enviado = False

    # Logging detallado
    clientes_emails = [cliente['email'] for cliente in correos_clientes] if correos_clientes else []
    datos_log = {
        "fecha_consulta": time.strftime("%Y-%m-%d %H:%M:%S"),
        "numero_radicado": numero_radicado,
        "fecha_radicado": resultado.get("fecha_radicado"),
        "fecha_ultima_actuacion": resultado.get("fecha_ultima_actuacion"),
        "despacho": resultado.get("despacho_departamento"),
        "demandante": demandante,
        "demandado": demandado,
        "actuacion_reciente": fecha_reciente if fecha_reciente else "No",
        "clientes_notificados": clientes_emails,
        "total_clientes": len(clientes_emails),
        "correo_enviado": correo_enviado,
        "mensaje": mensaje_log
    }
    log_scraping(datos_log)
    return resultado

def log_scraping(datos_log):
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs_scraper_colombia")
    os.makedirs(log_dir, exist_ok=True)
    now = time.strftime("%d-%m-%Y_%H.%M")
    log_filename = f"scraping_log_{now}.txt"
    log_path = os.path.join(log_dir, log_filename)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(datos_log, ensure_ascii=False) + "\n")

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
            
            # --- AJUSTE PARA GUARDAR FECHAS EN LA BD ---
            try:
                # Actualizar TODAS las radicaciones con este número (puede haber múltiples clientes)
                radicaciones = Radicacion.objects.filter(numero_radicado=numero_radicado)
                for radicacion in radicaciones:
                    radicacion.fecha_radicacion = datos.get('fecha_radicado')
                    radicacion.ultima_actuacion = datos.get('fecha_ultima_actuacion')
                    radicacion.despacho_departamento = datos.get('despacho_departamento')
                    radicacion.sujetos_procesales = datos.get('sujetos_procesales')
                    radicacion.save()
                print(f"✅ Actualizadas {radicaciones.count()} radicaciones para número {numero_radicado}")
            except Exception as e:
                print(f"❌ Error actualizando radicación {numero_radicado}: {e}")
            # -------------------------------------------
            
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