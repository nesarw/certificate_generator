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
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_name_overlay(name, width, height):
    """Create a PDF with just the name to overlay on the template."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(letter))
    
    # Add name (centered) with italic font
    c.setFont("Helvetica-Oblique", 39)
    c.setFillColor(HexColor("#000000"))
    name_width = c.stringWidth(name, "Helvetica-Oblique", 39)
    c.drawString(width/2 + 30 - name_width/2, height/2 - 50, name)
    
    c.save()
    packet.seek(0)
    return packet

def generate_certificate(name, template_data):
    """Generate a certificate by adding name to the template."""
    # Create PDF with name
    width, height = landscape(letter)
    name_pdf = create_name_overlay(name, width, height)
    
    # Read the template from bytes
    template = PdfReader(io.BytesIO(template_data))
    name_layer = PdfReader(name_pdf)
    
    # Merge template with name
    output = PdfWriter()
    page = template.pages[0]
    page.merge_page(name_layer.pages[0])
    output.add_page(page)
    
    # Save the result to bytes
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    return output_stream.getvalue()

def send_email(recipient_email, recipient_name, certificate_data):
    """Send email with certificate attachment."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = os.getenv('SENDER_EMAIL')
        msg["To"] = recipient_email
        msg["Subject"] = "Your Certificate of Achievement"
        
        # Add body
        body = f"""
        Dear {recipient_name},

        Congratulations! Please find attached your Certificate of Achievement.

        Best regards,
        Nesar Wagannawar
        """
        msg.attach(MIMEText(body, "plain"))
        
        # Attach certificate
        pdf = MIMEApplication(certificate_data, _subtype="pdf")
        pdf.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"{recipient_name.replace(' ', '_')}_certificate.pdf"
        )
        msg.attach(pdf)
        
        # Send email
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
            
        print(f"Successfully sent certificate to {recipient_email}")
        
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {str(e)}")
        raise

def main():
    """Main function to process the Excel file and generate certificates."""
    # Initialize S3 client
    s3 = boto3.client(
        's3',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN')
    )
    
    # Download template from S3
    try:
        response = s3.get_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key='templates/Certificates.pdf'
        )
        template_data = response['Body'].read()
    except ClientError as e:
        print(f"Error downloading template: {e}")
        return
    
    # Download participants file from S3
    try:
        response = s3.get_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key='data/participants.xlsx'
        )
        df = pd.read_excel(io.BytesIO(response['Body'].read()))
    except ClientError as e:
        print(f"Error downloading participants file: {e}")
        return
    
    # Process each participant
    for _, row in df.iterrows():
        name = row["name"]
        email = row["email"]
        
        try:
            # Generate certificate
            certificate_data = generate_certificate(name, template_data)
            
            # Upload to S3
            certificate_filename = f"{name.replace(' ', '_')}_certificate.pdf"
            s3.put_object(
                Bucket=os.getenv('S3_BUCKET_NAME'),
                Key=f"generated_certificates/{certificate_filename}",
                Body=certificate_data
            )
            print(f"Generated and uploaded certificate for {name}")
            
            # Send email
            send_email(email, name, certificate_data)
            
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    main() 