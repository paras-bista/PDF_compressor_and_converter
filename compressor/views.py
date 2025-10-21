import os
import datetime
import re
from django.shortcuts import render
from django.http import FileResponse
from PyPDF2 import PdfReader, PdfWriter

MEDIA_FOLDER = "media/compressed_pdfs/"

# 🔹 Function to clean filenames (remove special characters)
def clean_filename(filename):
    return re.sub(r'[^\w.-]', '_', filename)

# 🔹 Ensure session-specific folder exists and return its path
def get_session_folder(session):
    if not session.session_key:
        session.save()
    session_key = session.session_key
    session_dir = os.path.join(MEDIA_FOLDER, session_key)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

# 🔹 Compress and merge PDFs
def compress_pdfs(pdf_files, output_dir):
    """Merge and compress multiple PDFs into one and store in output_dir."""
    writer = PdfWriter()
    for pdf in pdf_files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            try:
                page.compress_content_streams()
            except Exception:
                pass
            writer.add_page(page)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    compressed_filename = f"compressed_{timestamp}.pdf"
    os.makedirs(output_dir, exist_ok=True)
    compressed_path = os.path.join(output_dir, compressed_filename)

    with open(compressed_path, "wb") as output_pdf:
        writer.write(output_pdf)

    return compressed_filename

# 🔹 Upload handler
def upload_files(request):
    """Handle PDF uploads and compress them. History is per-session (device)."""
    session_folder = get_session_folder(request.session)

    if request.method == "POST":
        files = request.FILES.getlist("files")
        if not files:
            return render(request, "compressor/upload.html", {"error": "Please upload at least one file."})

        pdf_paths = []
        for uploaded in files:
            ext = uploaded.name.split(".")[-1].lower()
            if ext != "pdf":
                return render(request, "compressor/upload.html", {"error": f"Unsupported file type: {uploaded.name}"})

            safe_filename = clean_filename(uploaded.name)
            temp_path = os.path.join(session_folder, safe_filename)

            with open(temp_path, "wb") as f:
                for chunk in uploaded.chunks():
                    f.write(chunk)
            pdf_paths.append(temp_path)

        compressed_filename = compress_pdfs(pdf_paths, output_dir=session_folder)

        # store per-session history
        history = request.session.get("compressed_files", [])
        history.append(compressed_filename)
        request.session["compressed_files"] = history
        request.session.modified = True

        return render(request, "compressor/result.html", {"compressed_filename": compressed_filename})

    # GET: show only this session's compressed files
    compressed_files = request.session.get("compressed_files", [])
    return render(request, "compressor/upload.html", {"compressed_files": compressed_files})

# 🔹 Download handler
def download_compressed(request, filename):
    """Serve the compressed PDF file for download only if it belongs to this session."""
    session_history = request.session.get("compressed_files", [])
    if filename not in session_history:
        return render(request, "compressor/result.html", {"error": "File not available for this session/device."})

    session_folder = get_session_folder(request.session)
    file_path = os.path.join(session_folder, filename)

    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)

    return render(request, "compressor/result.html", {"error": "Compressed file not found."})
