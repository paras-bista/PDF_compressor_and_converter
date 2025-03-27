import os
import datetime
import pythoncom
import re
from django.shortcuts import render
from django.http import FileResponse
from PyPDF2 import PdfReader, PdfWriter
import comtypes.client
import win32com.client

MEDIA_FOLDER = "media/compressed_pdfs/"

# 🔹 Function to clean filenames (remove special characters)
def clean_filename(filename):
    return re.sub(r'[^\w.-]', '_', filename)

def convert_docx_to_pdf(docx_path, pdf_path):
    """Convert Word file (.docx) to PDF using MS Word."""
    pythoncom.CoInitialize()
    word = comtypes.client.CreateObject("Word.Application")
    word.Visible = False

    # 🔹 Ensure file exists before opening
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"File not found: {docx_path}")

    doc = word.Documents.Open(os.path.abspath(docx_path))
    doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)  # 17 is the PDF format
    doc.Close()
    word.Quit()
    pythoncom.CoUninitialize()

def convert_excel_to_pdf(excel_path, pdf_path):
    """Convert Excel file (.xlsx) to PDF using MS Excel."""
    pythoncom.CoInitialize()
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False

    # 🔹 Ensure file exists before opening
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"File not found: {excel_path}")

    wb = excel.Workbooks.Open(os.path.abspath(excel_path))
    wb.ExportAsFixedFormat(0, os.path.abspath(pdf_path))  # 0 = PDF format
    wb.Close()
    excel.Quit()
    pythoncom.CoUninitialize()

def compress_pdfs(pdf_files):
    """Merge and compress multiple PDFs into one."""
    writer = PdfWriter()
    for pdf in pdf_files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    compressed_filename = f"compressed_{timestamp}.pdf"
    compressed_path = os.path.join(MEDIA_FOLDER, compressed_filename)

    os.makedirs(os.path.dirname(compressed_path), exist_ok=True)

    with open(compressed_path, "wb") as output_pdf:
        writer.write(output_pdf)

    return compressed_filename

def upload_files(request):
    """Handle file uploads and convert to compressed PDF."""
    if request.method == "POST":
        files = request.FILES.getlist("files")
        
        if not files:
            return render(request, "compressor/upload.html", {"error": "Please upload at least one file."})

        pdf_paths = []
        for file in files:
            ext = file.name.split(".")[-1].lower()
            safe_filename = clean_filename(file.name)  # 🔹 Clean filename
            temp_path = os.path.join(MEDIA_FOLDER, f"temp_{safe_filename}")

            with open(temp_path, "wb") as f:
                f.write(file.read())

            if ext == "pdf":
                pdf_paths.append(temp_path)
            elif ext == "docx":
                pdf_path = temp_path.replace(".docx", ".pdf")
                convert_docx_to_pdf(temp_path, pdf_path)
                pdf_paths.append(pdf_path)
            elif ext in ["xls", "xlsx"]:
                pdf_path = temp_path.replace(".xlsx", ".pdf").replace(".xls", ".pdf")
                convert_excel_to_pdf(temp_path, pdf_path)
                pdf_paths.append(pdf_path)

        compressed_filename = compress_pdfs(pdf_paths)

        return render(request, "compressor/result.html", {"compressed_filename": compressed_filename})

    compressed_files = os.listdir(MEDIA_FOLDER) if os.path.exists(MEDIA_FOLDER) else []

    return render(request, "compressor/upload.html", {"compressed_files": compressed_files})

def download_compressed(request, filename):
    """Serve the compressed PDF file for download."""
    file_path = os.path.join(MEDIA_FOLDER, filename)
    
    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)

    return render(request, "compressor/result.html", {"error": "Compressed file not found."})
