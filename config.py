import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, landscape

# Load environment variables
load_dotenv()

# Get landscape dimensions
width, height = landscape(letter)

# File paths
CERTIFICATE_TEMPLATE = "templates/ Certificates.pdf"  # Updated path with exact filename including space
EXCEL_FILE = "data/participants.xlsx"
OUTPUT_DIR = "generated_certificates"

# Certificate text settings
NAME_FONT_SIZE = 39
NAME_COLOR = "#000000"  # Black color for better visibility on template
NAME_POSITION = {
    "x": width/2 + 30,  # Center of page + 50px right (increased from 20)
    "y": height/2 - 50  # Middle of page - 50px down
}

# Email settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# Email template
EMAIL_SUBJECT = "Your Certificate of Achievement"
EMAIL_BODY = """
Dear {name},

Congratulations! Please find attached your Certificate of Achievement.

Best regards,
Nesar Wagannawar
""" 