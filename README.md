# PDF Compressor & Converter

A Django-based project that enables you to:
- **Convert Word and Excel files** to PDF.
- **Compress any file** and produce a PDF as the final output.

## Features

- **Word (DOCX) → PDF** conversion
- **Excel (XLSX) → PDF** conversion
- **File compression** for any file type with PDF output
- Simple, user-friendly **web-based** interface

 PDFCOMPRESSOR/
├── compressor/        # Django app for file conversion and compression
│   ├── __pycache__/   # Compiled Python files
│   ├── migrations/    # Database migrations
│   ├── templates/     # HTML templates
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py      # Database models
│   ├── tests.py       # Unit tests
│   ├── urls.py        # URL routing for the app
│   └── views.py       # Application logic
├── media/             # Directory for uploaded and processed files
├── pdf_compressor/    # Project-level settings and configuration
├── db.sqlite3         # SQLite database (if used)
└── manage.py          # Django’s command-line utility


## Installation

1. **Clone the Repository**

   ```sh
   git clone <YOUR-REPO-URL>
   cd PDFCOMPRESSOR
2.Create a Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3.Install Dependencies
pip install -r requirements.txt

4.Apply Database Migrations
python manage.py migrate

5.Run the Development Server
python manage.py runserver
Open your browser and visit: http://127.0.0.1:8000/


