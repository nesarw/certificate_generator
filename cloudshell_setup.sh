#!/bin/bash

# Create project directory
mkdir -p certificate_generator
cd certificate_generator

# Create necessary directories
mkdir -p templates data

# Create requirements.txt
cat > requirements.txt << 'EOL'
pandas==2.2.1
reportlab==4.1.0
Pillow==10.2.0
openpyxl==3.1.2
python-dotenv==1.0.1
PyPDF2==3.0.1
boto3==1.34.69
botocore==1.34.69
EOL

# Create aws_config.py
cat > aws_config.py << 'EOL'
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
EOL

# Create aws_services.py
cat > aws_services.py << 'EOL'
import boto3
import io
from botocore.exceptions import ClientError
import aws_config

class AWSServices:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=aws_config.AWS_REGION,
            aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=aws_config.AWS_SESSION_TOKEN
        )
        
        self.ses_client = boto3.client(
            'ses',
            region_name=aws_config.SES_REGION,
            aws_access_key_id=aws_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=aws_config.AWS_SESSION_TOKEN
        )

    def download_template(self):
        """Download certificate template from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=aws_config.S3_BUCKET_NAME,
                Key=aws_config.S3_TEMPLATE_PATH
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading template: {e}")
            raise

    def upload_certificate(self, certificate_data, filename):
        """Upload generated certificate to S3"""
        try:
            self.s3_client.put_object(
                Bucket=aws_config.S3_BUCKET_NAME,
                Key=f"{aws_config.S3_OUTPUT_PREFIX}{filename}",
                Body=certificate_data
            )
            return f"https://{aws_config.S3_BUCKET_NAME}.s3.amazonaws.com/{aws_config.S3_OUTPUT_PREFIX}{filename}"
        except ClientError as e:
            print(f"Error uploading certificate: {e}")
            raise

    def send_email(self, recipient_email, recipient_name, certificate_url):
        """Send email using AWS SES"""
        try:
            response = self.ses_client.send_email(
                Source=aws_config.SES_SENDER_EMAIL,
                Destination={
                    'ToAddresses': [recipient_email]
                },
                Message={
                    'Subject': {
                        'Data': 'Your Certificate of Achievement'
                    },
                    'Body': {
                        'Text': {
                            'Data': f"""
                            Dear {recipient_name},

                            Congratulations! Your certificate is ready. You can download it from:
                            {certificate_url}

                            Best regards,
                            Certificate Generator Team
                            """
                        }
                    }
                }
            )
            return response['MessageId']
        except ClientError as e:
            print(f"Error sending email: {e}")
            raise
EOL

# Create setup_aws.py
cat > setup_aws.py << 'EOL'
import boto3
import os
import json
from botocore.exceptions import ClientError
import pandas as pd
from dotenv import load_dotenv
import time

def create_s3_bucket(bucket_name, region):
    """Create S3 bucket if it doesn't exist"""
    s3 = boto3.client('s3', region_name=region)
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Created S3 bucket: {bucket_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists")
        else:
            print(f"Error creating bucket: {e}")
            raise

def create_sample_files():
    """Create sample template and participants file"""
    # Create directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Create sample participants Excel file
    df = pd.DataFrame({
        'name': ['John Doe', 'Jane Smith'],
        'email': ['john@example.com', 'jane@example.com']
    })
    df.to_excel('data/participants.xlsx', index=False)
    print("Created sample participants.xlsx")
    
    # Create a simple PDF template
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape
    
    c = canvas.Canvas('templates/Certificates.pdf', pagesize=landscape(letter))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 400, "Certificate of Achievement")
    c.setFont("Helvetica", 16)
    c.drawString(100, 350, "This is to certify that")
    c.drawString(100, 300, "_____________________")
    c.drawString(100, 250, "has successfully completed the course")
    c.save()
    print("Created sample certificate template")

def upload_files_to_s3(bucket_name, region):
    """Upload files to S3"""
    s3 = boto3.client('s3', region_name=region)
    
    # Upload template
    try:
        s3.upload_file('templates/Certificates.pdf', bucket_name, 'templates/Certificates.pdf')
        print("Uploaded certificate template to S3")
    except ClientError as e:
        print(f"Error uploading template: {e}")
        raise
    
    # Upload participants file
    try:
        s3.upload_file('data/participants.xlsx', bucket_name, 'data/participants.xlsx')
        print("Uploaded participants file to S3")
    except ClientError as e:
        print(f"Error uploading participants file: {e}")
        raise

def update_env_file(aws_region, access_key, secret_key, session_token, bucket_name, sender_email):
    """Update .env file with AWS credentials"""
    env_content = f"""# AWS Configuration
AWS_REGION={aws_region}
AWS_ACCESS_KEY_ID={access_key}
AWS_SECRET_ACCESS_KEY={secret_key}
AWS_SESSION_TOKEN={session_token}
S3_BUCKET_NAME={bucket_name}
SES_SENDER_EMAIL={sender_email}

# Note: SES is not available in this environment
# You can use SMTP for email sending instead
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
"""
    with open('.env', 'w') as f:
        f.write(env_content)
    print("Updated .env file with AWS credentials")

def main():
    # AWS Credentials
    aws_region = 'us-east-1'
    aws_access_key = 'YOUR_AWS_ACCESS_KEY'
    aws_secret_key = 'YOUR_AWS_SECRET_KEY'
    aws_session_token = 'YOUR_AWS_SESSION_TOKEN'
    
    # Generate unique bucket name with timestamp
    timestamp = int(time.time())
    bucket_name = f'certificate-generator-{timestamp}'
    sender_email = 'your_email@gmail.com'
    
    print("Starting setup process...")
    print(f"Using bucket name: {bucket_name}")
    
    # Create sample files
    create_sample_files()
    
    # Create S3 bucket
    create_s3_bucket(bucket_name, aws_region)
    
    # Upload files to S3
    upload_files_to_s3(bucket_name, aws_region)
    
    # Update .env file
    update_env_file(aws_region, aws_access_key, aws_secret_key, aws_session_token, bucket_name, sender_email)
    
    print("\nSetup completed!")
    print("Note: SES is not available in this environment. The script will use SMTP for email sending instead.")
    print("You can now run the certificate generator script.")

if __name__ == "__main__":
    main()
EOL

# Install required packages
pip install -r requirements.txt

# Make the script executable
chmod +x setup_aws.py

echo "Setup completed! Now you can run:"
echo "python setup_aws.py" 
