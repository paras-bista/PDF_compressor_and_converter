from django.db import models

# Create your models here.

class PDFFile(models.Model):
    file = models.FileField(upload_to="pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
