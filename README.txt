# Vigilance Awareness Certificate Download Portal

A small Flask website that lets a participant enter their registered 10-digit mobile number and download the matching PDF certificate.

## Files
- `app.py` — Flask application
- `templates/index.html` — responsive portal page
- `mapping.json` — maps mobile numbers to PDF filenames
- `certificates/` — put the actual certificate PDFs here
- `requirements.txt` — Python dependency

## Setup on Windows
1. Install Python 3.10 or newer.
2. Extract this ZIP to a folder.
3. Open Command Prompt in that folder.
4. Run:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   py app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

## Add your real certificates
1. Copy each PDF certificate into the `certificates` folder.
2. Open `mapping.json` in Notepad.
3. Replace the sample entry with the actual registered mobile number and exact PDF filename.

Example:
```json
{
  "9876543210": "Amit-Sharma.pdf",
  "9123456780": "Priya-Verma.pdf"
}
```

Important:
- Mobile numbers must be unique in `mapping.json`.
- The PDF filename must match exactly, including spaces and capital letters.
- Delete the sample entry before publishing; it is only an example and its PDF is not included.
- Do not upload real participants' mobile numbers or certificates to a public code repository.
- Use HTTPS and appropriate access controls for public hosting. Mobile number alone is not strong identity verification for sensitive certificates.
- `py app.py` is for local testing. On a hosting platform, follow its production start-command instructions (typically a WSGI server such as Gunicorn on Linux).
