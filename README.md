# Certificate Generator and Emailer

This Python project automatically generates personalized certificates from a template and emails them to participants listed in an Excel file.

## Features

- Reads participant data from an Excel file
- Generates personalized PDF certificates
- Emails certificates to participants
- Configurable certificate text position and styling
- Secure email sending using SMTP

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your email credentials:
     - For Gmail:
       1. Enable 2-Step Verification in your Google Account
       2. Generate an App Password:
          - Go to Google Account settings
          - Security
          - App Passwords (under 2-Step Verification)
          - Select "Mail" and your device
          - Use the generated 16-character password
       3. Update the .env file with your email and App Password

3. Prepare your files:
   - Place your certificate template PDF in the `templates` folder as `Certificates.pdf`
   - Create an Excel file in the `data` folder named `participants.xlsx` with columns:
     - `name`: Participant's full name
     - `email`: Participant's email address

## Security Notes

1. Never commit your `.env` file to version control
2. The `.env` file is listed in `.gitignore` to prevent accidental commits
3. Use `.env.example` as a template for required environment variables
4. Always use App Passwords for Gmail, never your account password
5. Keep your credentials secure and never share them

## Directory Structure

```
.
├── README.md
├── requirements.txt
├── config.py
├── certificate_generator.py
├── .env.example
├── .gitignore
├── templates/
│   └── Certificates.pdf
├── data/
│   └── participants.xlsx
└── generated_certificates/
    └── (generated certificates)
```

## Usage

1. Update `participants.xlsx` with participant information
2. Run the script:
   ```bash
   python3 certificate_generator.py
   ```

## Configuration

You can customize:
- Certificate template
- Text position and styling
- Email subject and body
- File paths and naming conventions

All settings can be adjusted in the `config.py` file.

## Error Handling

The script includes error handling for:
- Missing files
- Invalid Excel format
- Certificate generation issues
- Email sending failures

Each error will be logged to the console while allowing the script to continue processing other participants.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Security

- Never commit sensitive information
- Always use environment variables for credentials
- Keep your App Passwords secure
- Regularly rotate your credentials
- Monitor your application's access and usage
