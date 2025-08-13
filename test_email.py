#!/usr/bin/env python3
"""
Script de test para verificar la configuración SMTP usando smtplib estándar
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración SMTP
SMTP_SERVER = "email.sphyrnasolutions.com"
SMTP_USERNAME = "system@delarueda.es"
SMTP_PASSWORD = "YoLoSe174591!"
FROM_EMAIL = "system@delarueda.es"
FROM_NAME = "Sistema de Contratos - De La Rueda"

def test_smtp_connection():
    """Test básico de conexión SMTP con smtplib"""
    print(f"Probando conexión SMTP a {SMTP_SERVER}")
    
    # Test de conectividad básica
    try:
        print("\n=== Test de conectividad básica ===")
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((SMTP_SERVER, 465))
        if result == 0:
            print("✅ Puerto 465 está abierto")
        else:
            print("❌ Puerto 465 cerrado o no accesible")
        sock.close()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((SMTP_SERVER, 587))
        if result == 0:
            print("✅ Puerto 587 está abierto")
        else:
            print("❌ Puerto 587 cerrado o no accesible")
        sock.close()
    except Exception as e:
        print(f"❌ Error test conectividad: {e}")
    
    # Intento 1: SSL directo (puerto 465)
    try:
        print("\n=== Intento 1: SSL directo (puerto 465) ===")
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context)
        print("✅ Conexión SSL establecida")
        print(f"Respuesta del servidor: {server.ehlo()}")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("✅ Login exitoso!")
        server.quit()
        return "ssl", 465
    except Exception as e:
        print(f"❌ Error SSL: {e}")
    
    # Intento 2: STARTTLS (puerto 587)
    try:
        print("\n=== Intento 2: STARTTLS (puerto 587) ===")
        server = smtplib.SMTP(SMTP_SERVER, 587)
        print("✅ Conexión inicial establecida")
        print(f"Respuesta del servidor: {server.ehlo()}")
        server.starttls()
        print("✅ STARTTLS exitoso")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("✅ Login exitoso!")
        server.quit()
        return "starttls", 587
    except Exception as e:
        print(f"❌ Error STARTTLS: {e}")
    
    # Intento 3: Puerto 25 con STARTTLS
    try:
        print("\n=== Intento 3: Puerto 25 con STARTTLS ===")
        server = smtplib.SMTP(SMTP_SERVER, 25)
        print("✅ Conexión inicial establecida")
        print(f"Respuesta del servidor: {server.ehlo()}")
        if server.has_extn('STARTTLS'):
            server.starttls()
            print("✅ STARTTLS exitoso")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("✅ Login exitoso!")
        server.quit()
        return "starttls", 25
    except Exception as e:
        print(f"❌ Error puerto 25: {e}")
    
    return None, None

def send_test_email(connection_type, port):
    """Envía un email de prueba"""
    print(f"\n=== Enviando email de prueba usando {connection_type} en puerto {port} ===")
    
    # Crear mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = "Test Email - Sistema de Contratos"
    message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    message["To"] = "admin@sphyrnasolutions.com"
    
    # Contenido HTML
    html_content = f"""
    <html>
      <body>
        <h2>Test Email</h2>
        <p>Este es un email de prueba del sistema de contratos.</p>
        <p>Si recibes este email, la configuración SMTP está funcionando correctamente.</p>
        <p>Método de conexión: {connection_type} en puerto {port}</p>
        <p>Enviado desde: {FROM_EMAIL}</p>
      </body>
    </html>
    """
    
    html_part = MIMEText(html_content, "html", "utf-8")
    message.attach(html_part)
    
    try:
        if connection_type == "ssl":
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(SMTP_SERVER, port, context=context)
        else:
            server = smtplib.SMTP(SMTP_SERVER, port)
            server.starttls()
        
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)
        server.quit()
        
        print("✅ Email enviado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

def main():
    print("🧪 Iniciando test de configuración SMTP con smtplib...")
    
    # Test de conexión
    connection_type, port = test_smtp_connection()
    
    if connection_type:
        print(f"\n✅ Conexión exitosa usando: {connection_type} en puerto {port}")
        
        # Test de envío de email
        success = send_test_email(connection_type, port)
        
        if success:
            print("\n🎉 Test completo exitoso! El sistema de email está funcionando.")
            print(f"Configuración recomendada: {connection_type} en puerto {port}")
        else:
            print("\n❌ La conexión funciona pero hay problemas enviando emails.")
    else:
        print("\n❌ No se pudo establecer conexión con ningún método.")
        print("\nVerifica:")
        print("- Servidor SMTP: " + SMTP_SERVER)
        print("- Usuario: " + SMTP_USERNAME)
        print("- Contraseña: " + ("*" * len(SMTP_PASSWORD)))

if __name__ == "__main__":
    main()