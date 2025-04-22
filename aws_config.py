import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

# S3 Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_TEMPLATE_PATH = 'templates/Certificates.pdf'
S3_OUTPUT_PREFIX = 'generated_certificates/'

# SES Configuration
SES_SENDER_EMAIL = os.getenv('SES_SENDER_EMAIL')
SES_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Optional RDS Configuration
RDS_ENDPOINT = os.getenv('RDS_ENDPOINT')
RDS_PORT = os.getenv('RDS_PORT', '3306')
RDS_DATABASE = os.getenv('RDS_DATABASE')
RDS_USERNAME = os.getenv('RDS_USERNAME')
RDS_PASSWORD = os.getenv('RDS_PASSWORD') 