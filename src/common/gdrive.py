from distutils.command.upload import upload
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def upload_file(file_path : str) -> str:
    g_auth = GoogleAuth()           
    g_drive = GoogleDrive(g_auth)  
    upload_slug = None
    return upload_slug

