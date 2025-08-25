import os
import textwrap
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from reportlab.lib.units import cm
from PIL import Image


# PDF Configuration
DESIGN_IMAGE_WIDTH = 13 * cm  # Standard width for design images (reducido de 15cm a 13cm para más espacio de texto)
DESIGN_IMAGE_MAX_HEIGHT = 13 * cm  # Maximum height for design images (reducido de 15cm a 13cm)
LOGO_WIDTH = 3 * cm  # Company logo width (reduced for more discretion)
LOGO_PATH = "storage/logo.png"  # Path to company logo

def format_date_spanish(date_str: str) -> str:
    """Convert date string to Spanish format for contract"""
    try:
        from datetime import datetime
        # Parse date string (format: dd/mm/yyyy hh:mm)
        if '/' in date_str and len(date_str) > 10:
            date_part = date_str.split(' ')[0]  # Get only date part
            day, month, year = date_part.split('/')
        else:
            # Fallback for other formats
            return f"_____ de _______ de {datetime.now().year}"
        
        months_spanish = [
            "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        
        month_name = months_spanish[int(month)]
        return f"{int(day)} de {month_name} de {year}"
    except:
        # Fallback if parsing fails
        from datetime import datetime
        return f"_____ de _______ de {datetime.now().year}"


def create_professional_pdf(pdf_path: str, client_name: str, client_email: str, design_image_path: str, 
                          titulo_diseno: str = None, puesto_empresa: str = None, politica_confirmacion: str = None,
                          signature_path: str = None, signed_by: str = None, signed_at_str: str = None):
    """Genera un PDF de aceptación de diseño personalizado en formato vertical"""
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Marca de agua se dibujará al final para aparecer por encima
    
    # Márgenes optimizados para aprovechar mejor el ancho
    margin_x = 1.5 * cm  # Reducido de 2cm a 1.5cm para más ancho de texto
    current_y = height - 1.5 * cm  # Más espacio aprovechable
    
    # Encabezado principal
    try:
        c.setFont("Esther-Medium", 14)
    except:
        c.setFont("Helvetica-Bold", 14)
    main_title = f"PRUEBA DISEÑO {client_name.upper()}" if titulo_diseno is None else titulo_diseno.upper()
    c.drawCentredString(width / 2, current_y, main_title)
    current_y -= 1.0 * cm  # Espacio equilibrado después del título
    
    # Logo de la empresa centrado (después del título)
    try:
        if os.path.exists(LOGO_PATH):
            logo_img = Image.open(LOGO_PATH)
            logo_width, logo_height = logo_img.size
            logo_aspect = logo_width / logo_height
            
            display_logo_width = LOGO_WIDTH
            display_logo_height = display_logo_width / logo_aspect
            
            logo_x = (width - display_logo_width) / 2
            logo_y = current_y - display_logo_height
            
            c.drawImage(LOGO_PATH, logo_x, logo_y, width=display_logo_width, height=display_logo_height)
            current_y = logo_y - 0.8 * cm  # Espacio después del logo
        else:
            current_y -= 0.5 * cm  # Espacio mínimo si no hay logo
    except Exception:
        current_y -= 0.5 * cm  # Espacio mínimo si hay error
    
    # Imagen del diseño con tamaño estándar
    try:
        img = Image.open(design_image_path)
        
        # Convertir PNG con transparencia a RGB con fondo blanco
        processed_image_path = design_image_path  # Por defecto usar la original
        temp_file = None
        
        if img.mode in ('RGBA', 'LA', 'P'):
            # Crear una imagen con fondo blanco
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
            
            # Guardar imagen procesada en archivo temporal
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            img.save(temp_file.name, 'JPEG', quality=95)
            processed_image_path = temp_file.name
            temp_file.close()
        elif img.mode != 'RGB':
            img = img.convert('RGB')
            # Guardar imagen convertida en archivo temporal
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            img.save(temp_file.name, 'JPEG', quality=95)
            processed_image_path = temp_file.name
            temp_file.close()
            
        img_width, img_height = img.size
        aspect = img_width / img_height
        
        # Tamaño estándar: ancho fijo, altura proporcional con límite
        display_width = DESIGN_IMAGE_WIDTH
        display_height = display_width / aspect
        
        # Aplicar límite máximo de altura
        if display_height > DESIGN_IMAGE_MAX_HEIGHT:
            display_height = DESIGN_IMAGE_MAX_HEIGHT
            display_width = display_height * aspect
        
        # Centrar imagen
        img_x = (width - display_width) / 2
        img_y = current_y - display_height
        
        # Usar imagen procesada
        c.drawImage(processed_image_path, img_x, img_y, width=display_width, height=display_height)
        
        # Limpiar archivo temporal si se creó
        if temp_file and os.path.exists(processed_image_path) and processed_image_path != design_image_path:
            try:
                os.unlink(processed_image_path)
            except:
                pass
        current_y = img_y - 0.8 * cm  # Espacio después de la imagen del diseño
    except Exception as e:
        c.setFont("Helvetica", 10)
        c.drawString(margin_x, current_y, f"[Error al insertar imagen: {e}]")
        current_y -= 1 * cm
    
    # Definir posición de la caja de firma
    box_height = 3 * cm  # Altura de la caja de firma (volvemos a 3cm)
    box_y = 1.5 * cm  # Posición desde el borde inferior
    
    # Calcular posición de la política: empezar justo encima de la caja
    policy_gap = 0.3 * cm  # Espacio mínimo entre política y caja
    policy_end_y = box_y + box_height + policy_gap
    
    # La política debe ocupar el espacio entre la imagen y la caja
    available_space = current_y - policy_end_y
    
    # Política de confirmación: empezar desde policy_end_y hacia arriba
    policy_start_y = policy_end_y
    if politica_confirmacion:
        legal_text = politica_confirmacion
    else:
        legal_text = (
            "He leído y acepto el diseño dispuesto, así como el texto anterior.\n\n"
            "Les rogamos comprueben el diseño gráfico, textos, direcciones, números de teléfono, palabras..."
            " La aceptación de este diseño conlleva la impresión y puesta en marcha, y por lo tanto, la aceptación del presupuesto."
            " Cualquier corrección o error tipográfico no descubierto con anterioridad, correrá a cargo del cliente.\n\n"
            "Los tamaños finales y la posición pueden variar ligeramente, dependiendo de la técnica empleada, el corte y manipulado manual."
            " El tono de la tinta se asemejará a esta muestra. Los colores pueden variar según la técnica y maquinaria empleada."
            " Si requiere pantones específicos, comuníquelo con anterioridad. Su uso implica incremento de precio y está limitado a tiradas offset o serigrafía.\n\n"
            "Puede realizar una modificación previa a la aceptación sin coste. Nuevas modificaciones conllevan costes añadidos."
            " Los materiales y acabados (laminados, lacas, bordados) pueden alterar la percepción del color.\n\n"
            "CONSENTIMIENTO: Al firmar este documento, acepto que se registre mi dirección IP y datos de conexión para fines de verificación y trazabilidad legal del contrato."
        )
    
    # Ajustar tamaño de fuente más pequeño para mejor proporción
    if available_space < 4 * cm:
        font_size = 7  # Reducido de 8 a 7
        line_spacing = 0.25 * cm  # Reducido para comprimir más
    else:
        font_size = 8  # Reducido de 9 a 8
        line_spacing = 0.28 * cm  # Reducido para comprimir más
    
    # Intentar usar fuente Esther-Medium, fallback a Helvetica
    try:
        c.setFont("Esther-Medium", font_size)
    except:
        c.setFont("Helvetica", font_size)
    lines = textwrap.wrap(legal_text, 120)  # Aumentado de 110 a 120 caracteres por línea
    
    # Calcular cuántas líneas caben en el espacio disponible
    max_lines = int(available_space / line_spacing)
    if len(lines) > max_lines and max_lines > 0:
        lines = lines[:max_lines-1]  # Dejar espacio para "..."
        lines.append("...")
    
    # Calcular posición de inicio para que la política termine justo encima de la caja
    total_text_height = len(lines) * line_spacing
    policy_start_y = policy_end_y + total_text_height
    
    # Dibujar política de arriba hacia abajo, terminando cerca de la caja
    policy_y = policy_start_y
    for line in lines:
        if policy_y >= policy_end_y and policy_y <= current_y:  # Dentro del rango permitido
            c.drawString(margin_x, policy_y, line)
            policy_y -= line_spacing  # Bajar hacia la caja
        else:
            break
    
    # Caja de firma en la parte inferior (ya definida arriba)
    box_width = width - 3 * cm  # Ancho de la caja (ajustado a nuevos márgenes: 1.5cm * 2)
    
    # Dibujar caja con borde
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(margin_x, box_y, box_width, box_height, fill=0)
    
    # Contenido de la caja (más compacto)
    try:
        c.setFont("Esther-Medium", 8)
    except:
        c.setFont("Helvetica-Bold", 8)
    c.drawString(margin_x + 0.3 * cm, box_y + box_height - 0.5 * cm, "ACEPTACIÓN Y FIRMA")
    
    # Campos de firma en una línea compacta
    try:
        c.setFont("Esther-Medium", 7)
    except:
        c.setFont("Helvetica", 7)
    # Fecha - solo en PDFs sin firmar (evitar duplicación)
    if not signed_by and not signed_at_str:
        c.drawString(margin_x + 0.3 * cm, box_y + box_height - 1 * cm, "Málaga, a _____ de _______ de 2025")
    
    # Solo mostrar campos cuando hay firma digital
    # Si no hay firma, no mostrar campos vacíos
    
    # Si hay firma digital, mostrarla en la caja
    if signature_path and signed_by:
        try:
            c.setFont("Esther-Medium", 7)
        except:
            c.setFont("Helvetica-Bold", 7)
        # Organizar textos sin solapamiento en caja de 3cm (bajados un poco)
        c.drawString(margin_x + 0.3 * cm, box_y + box_height - 0.8 * cm, f"✓ Firmado por: {signed_by}")
        if puesto_empresa:
            c.drawString(margin_x + 0.3 * cm, box_y + box_height - 1.1 * cm, f"Puesto/Empresa: {puesto_empresa}")
        if signed_at_str:
            formatted_date = format_date_spanish(signed_at_str)
            c.drawString(margin_x + 0.3 * cm, box_y + 0.3 * cm, f"Málaga, a {formatted_date}")
        
        # Mostrar imagen de firma en la caja (muy pequeña)
        try:
            sig_img = Image.open(signature_path)
            sig_width, sig_height = sig_img.size
            sig_aspect_ratio = sig_height / sig_width
            sig_display_width = 8.0 * cm  # Firma ENORME y muy visible (aumentada de 5cm a 8cm)
            sig_display_height = sig_display_width * sig_aspect_ratio
            
            # Ajustar posición para firma ENORME en caja normal
            sig_x = margin_x + box_width - 8.5 * cm  # Más espacio para firma de 8cm
            sig_y = box_y + 0.2 * cm  # Posición baja en caja de 3cm
            
            c.drawImage(signature_path, sig_x, sig_y, 
                       width=sig_display_width, height=sig_display_height)
        except Exception:
            pass
    
    # Pie de página minimalista (solo información del cliente si es necesaria)
    try:
        c.setFont("Esther-Medium", 7)
    except:
        c.setFont("Helvetica", 7)
    c.drawString(margin_x, 0.5 * cm, f"Cliente: {client_name} | Email: {client_email}")
    
    # Marca de agua con logo (por encima de todo el contenido)
    c.saveState()
    try:
        if os.path.exists(LOGO_PATH):
            # Logo como marca de agua grande con opacidad muy sutil
            c.setFillAlpha(0.03)  # 3% de opacidad (muy sutil)
            
            # Procesar logo igual que las imágenes de diseño para manejar transparencia
            logo_img = Image.open(LOGO_PATH)
            
            # Convertir logo con transparencia a RGB con fondo blanco si es necesario
            processed_logo_path = LOGO_PATH  # Por defecto usar el original
            temp_logo_file = None
            
            if logo_img.mode in ('RGBA', 'LA', 'P'):
                # Crear una imagen con fondo blanco
                background = Image.new('RGB', logo_img.size, (255, 255, 255))
                if logo_img.mode == 'P':
                    logo_img = logo_img.convert('RGBA')
                background.paste(logo_img, mask=logo_img.split()[-1] if logo_img.mode in ('RGBA', 'LA') else None)
                logo_img = background
            elif logo_img.mode != 'RGB':
                logo_img = logo_img.convert('RGB')
            
            # Convertir a escala de grises para marca de agua más sutil
            logo_img = logo_img.convert('L').convert('RGB')
            
            # Guardar logo procesado en archivo temporal
            temp_logo_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            logo_img.save(temp_logo_file.name, 'JPEG', quality=95)
            processed_logo_path = temp_logo_file.name
            temp_logo_file.close()
            
            logo_width, logo_height = logo_img.size
            logo_aspect = logo_width / logo_height
            
            # Calcular tamaño grande para atravesar el documento completo
            if logo_aspect > (width / height):
                # Logo más ancho que la página - llenar el ancho completo
                watermark_width = width * 0.9  # 90% del ancho de página
                watermark_height = watermark_width / logo_aspect
            else:
                # Logo más alto que la página - llenar la altura completa
                watermark_height = height * 0.8  # 80% de la altura de página
                watermark_width = watermark_height * logo_aspect
            
            # Centrar en el documento para atravesarlo completamente
            watermark_x = (width - watermark_width) / 2
            watermark_y = (height - watermark_height) / 2
            
            c.drawImage(processed_logo_path, watermark_x, watermark_y, 
                       width=watermark_width, height=watermark_height)
            
            # Limpiar archivo temporal del logo si se creó
            if temp_logo_file and os.path.exists(processed_logo_path) and processed_logo_path != LOGO_PATH:
                try:
                    os.unlink(processed_logo_path)
                except:
                    pass
                    
    except Exception:
        pass  # Si hay error con el logo, continuar sin marca de agua
    c.restoreState()
    
    c.save()