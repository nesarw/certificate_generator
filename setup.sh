#!/bin/bash

# Create project directory
mkdir -p certificate_generator
cd certificate_generator

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

# Install required packages
pip install -r requirements.txt

# Copy setup script
cp ../setup_aws.py .

# Run setup script
python setup_aws.py 