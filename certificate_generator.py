import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from PyPDF2 import PdfReader, PdfWriter
import io
import config

def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)

def create_name_overlay(name, width, height):
    """Create a PDF with just the name to overlay on the template."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(letter))
    
    # Add name (centered) with italic font
    c.setFont("Helvetica-Oblique", config.NAME_FONT_SIZE)
    c.setFillColor(HexColor(config.NAME_COLOR))
    name_width = c.stringWidth(name, "Helvetica-Oblique", config.NAME_FONT_SIZE)
    c.drawString(config.NAME_POSITION["x"] - name_width/2, config.NAME_POSITION["y"], name)
    
    c.save()
    packet.seek(0)
    return packet

def generate_certificate(name, output_path):
    """Generate a certificate by adding name to the template."""
    # Create PDF with name
    width, height = landscape(letter)
    name_pdf = create_name_overlay(name, width, height)
    
    # Read the template
    template = PdfReader(open(config.CERTIFICATE_TEMPLATE, "rb"))
    name_layer = PdfReader(name_pdf)
    
    # Merge template with name
    output = PdfWriter()
    page = template.pages[0]
    page.merge_page(name_layer.pages[0])
    output.add_page(page)
    
    # Save the result
    with open(output_path, "wb") as outputStream:
        output.write(outputStream)

def send_email(recipient_email, recipient_name, certificate_path):
    """Send email with certificate attachment."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = config.SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = config.EMAIL_SUBJECT
        
        # Add body
        body = config.EMAIL_BODY.format(name=recipient_name)
        msg.attach(MIMEText(body, "plain"))
        
        # Attach certificate
        with open(certificate_path, "rb") as f:
            pdf = MIMEApplication(f.read(), _subtype="pdf")
            pdf.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(certificate_path)
            )
            msg.attach(pdf)
        
        # Send email
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)
            
        print(f"Successfully sent certificate to {recipient_email}")
        
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {str(e)}")
        raise

def main():
    """Main function to process the Excel file and generate certificates."""
    ensure_directories()
    
    # Check if template exists
    if not os.path.exists(config.CERTIFICATE_TEMPLATE):
        print(f"Error: Certificate template not found at {config.CERTIFICATE_TEMPLATE}")
        return
    
    # Check if Excel file exists
    if not os.path.exists(config.EXCEL_FILE):
        print(f"Error: Excel file not found at {config.EXCEL_FILE}")
        return
    
    # Read Excel file
    try:
        df = pd.read_excel(config.EXCEL_FILE)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    # Process each participant
    for _, row in df.iterrows():
        name = row["name"]
        email = row["email"]
        
        # Generate certificate filename
        certificate_filename = f"{name.replace(' ', '_')}_certificate.pdf"
        certificate_path = os.path.join(config.OUTPUT_DIR, certificate_filename)
        
        try:
            # Generate certificate
            generate_certificate(name, certificate_path)
            print(f"Generated certificate for {name}")
            
            # Send email
            send_email(email, name, certificate_path)
            
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    main() 