#!/usr/bin/env python
"""
Script para probar el envío de correos después de los cambios en el scraper
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_judicial.settings')
django.setup()

from notifications.email_sender import EmailSender
from clientes.models import Radicacion

def test_email_functionality():
    print("="*60)
    print("   PRUEBA DE FUNCIONALIDAD DE CORREOS")
    print("="*60)
    
    # Configuración del correo
    EMAIL = "tavo0132@gmail.com"
    PASSWORD = "jbuf phcp ymnp fhjy"
    sender = EmailSender(EMAIL, PASSWORD)
    
    print(f"📧 Configuración de correo: {EMAIL}")
    
    # Verificar si hay radicaciones duplicadas para probar
    print("\n--- VERIFICANDO RADICACIONES DUPLICADAS ---")
    from django.db.models import Count
    duplicados = Radicacion.objects.values('numero_radicado').annotate(
        count=Count('numero_radicado')
    ).filter(count__gt=1)
    
    if duplicados.exists():
        for dup in duplicados:
            numero = dup['numero_radicado']
            radicaciones = Radicacion.objects.filter(numero_radicado=numero)
            print(f"\n🔄 Número duplicado: {numero}")
            print(f"   Total clientes: {dup['count']}")
            
            for rad in radicaciones:
                print(f"   - {rad.cliente.first_name} {rad.cliente.last_name} ({rad.cliente.email})")
            
            # Probar envío de correo a estos clientes
            print(f"   📤 Probando envío de correos...")
            for rad in radicaciones:
                try:
                    asunto = f"[PRUEBA] Actualización Proceso - {numero}"
                    mensaje = f"""
                    <html>
                    <body>
                        <h2>Prueba de Notificación</h2>
                        <p>Hola <b>{rad.cliente.first_name}</b>,</p>
                        <p>Este es un correo de prueba para verificar que el sistema de notificaciones funciona correctamente con radicaciones duplicadas.</p>
                        <p><b>Número de radicado:</b> {numero}</p>
                        <p>Si recibe este correo, el sistema está funcionando correctamente.</p>
                        <br>
                        <p>Saludos,<br><b>Sistema Judicial</b></p>
                    </body>
                    </html>
                    """
                    
                    resultado = sender.enviar_correo(rad.cliente.email, asunto, mensaje, html=True)
                    if resultado:
                        print(f"   ✅ Correo enviado a {rad.cliente.email}")
                    else:
                        print(f"   ❌ Fallo al enviar a {rad.cliente.email}")
                except Exception as e:
                    print(f"   ❌ Error enviando a {rad.cliente.email}: {e}")
    else:
        print("⚠️  No se encontraron radicaciones duplicadas para probar")
        
        # Crear un ejemplo si no hay duplicados
        print("\n--- BUSCANDO RADICACIÓN ÚNICA PARA PRUEBA ---")
        radicacion = Radicacion.objects.first()
        if radicacion:
            print(f"🔍 Usando radicación: {radicacion.numero_radicado}")
            print(f"   Cliente: {radicacion.cliente.first_name} {radicacion.cliente.last_name}")
            print(f"   Email: {radicacion.cliente.email}")
            
            try:
                asunto = f"[PRUEBA] Sistema de Notificaciones - {radicacion.numero_radicado}"
                mensaje = f"""
                <html>
                <body>
                    <h2>Prueba de Sistema de Notificaciones</h2>
                    <p>Hola <b>{radicacion.cliente.first_name}</b>,</p>
                    <p>Este es un correo de prueba para verificar que el sistema de notificaciones funciona correctamente.</p>
                    <p><b>Número de radicado:</b> {radicacion.numero_radicado}</p>
                    <p>El sistema ha sido actualizado para manejar correctamente las notificaciones.</p>
                    <br>
                    <p>Saludos,<br><b>Sistema Judicial</b></p>
                </body>
                </html>
                """
                
                resultado = sender.enviar_correo(radicacion.cliente.email, asunto, mensaje, html=True)
                if resultado:
                    print(f"✅ Correo de prueba enviado exitosamente")
                else:
                    print(f"❌ Fallo al enviar correo de prueba")
            except Exception as e:
                print(f"❌ Error en prueba de correo: {e}")
    
    print("\n" + "="*60)
    print("   PRUEBA COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    test_email_functionality()
