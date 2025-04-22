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
                            Nesar Wagannawar
                            """
                        }
                    }
                }
            )
            return response['MessageId']
        except ClientError as e:
            print(f"Error sending email: {e}")
            raise 