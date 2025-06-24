import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def conectar_servidor(self):
        """Establece conexión con el servidor SMTP"""
        try:
            servidor = smtplib.SMTP(self.smtp_server, self.smtp_port)
            servidor.starttls()
            servidor.login(self.email, self.password)
            return servidor
        except Exception as e:
            print(f"Error al conectar: {str(e)}")
            return None

    def enviar_correo(self, destinatario, asunto, mensaje):
        """
        Envía un correo electrónico
        
        Args:
            destinatario (str): Dirección de correo del destinatario
            asunto (str): Asunto del correo
            mensaje (str): Contenido del correo
        """
        try:
            # Crear el objeto del mensaje
            email_msg = MIMEMultipart()
            email_msg['From'] = self.email
            email_msg['To'] = destinatario
            email_msg['Subject'] = asunto

            # Agregar el cuerpo del mensaje
            email_msg.attach(MIMEText(mensaje, 'plain'))

            # Conectar y enviar
            servidor = self.conectar_servidor()
            if servidor:
                servidor.send_message(email_msg)
                servidor.quit()
                print(f"Correo enviado exitosamente a {destinatario}")
                return True
            return False
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return False

# Ejemplo de uso:
if __name__ == "__main__":
    # Configuración del remitente
    EMAIL = "tavo0132@gmail.com"  # Reemplaza con tu correo
    PASSWORD = "emie yadk hozl dolp"      # Reemplaza con tu contraseña de aplicación

    # Crear instancia del enviador de correos
    sender = EmailSender(EMAIL, PASSWORD)

    # Datos del correo
    destinatario = "tavo0132@gmail.com"
    asunto = f"Notificación - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    mensaje = """
    Hola,
    
    Esta es una notificación automática enviada desde Python.
    
    Saludos,
    Tu Sistema de Notificaciones
    """

    # Enviar el correo
    sender.enviar_correo(destinatario, asunto, mensaje)
