from django.urls import path
from .views import upload_files, download_compressed

urlpatterns = [
    path("", upload_files, name="upload_files"),
    path("download/<str:filename>/", download_compressed, name="download_compressed"),
]
