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
