import os
from flask import Blueprint, request, current_app
from print_api.common.routing import custom_response
from print_api.common.gdrive import GoogleDriveUploader


file_upload_api = Blueprint("file_upload", __name__)

@file_upload_api.route("/upload_stl", methods=["POST"])
def upload_stl():
    """
    API Route to upload an STL file to the server
    """

    if 'file' not in request.files:
        current_app.logger.error("No file part in the request")
        return custom_response(status_code=400, details="No file part")

    file = request.files['file']

    if file.filename == '':
        current_app.logger.error("File name is empty")
        return custom_response(status_code=400, details="File name is empty")

    if file:
        file_type = file.filename.split(".")[-1]

        if file_type not in ["stl", "3mf", "obj"]:
            current_app.logger.error(f"File type {file_type} not allowed")
            return custom_response(status_code=400, details="File type not allowed")

        return upload_file_with_catches(file, "stls")
    else:
        current_app.logger.error("No file in the request")
        return custom_response(status_code=400, details="No file in the request")


@file_upload_api.route("/upload_gcode", methods=["POST"])
def upload_gcode():
    """
    API Route to upload an STL file to the server
    """

    if 'file' not in request.files:
        current_app.logger.error("No file part in the request")
        return custom_response(status_code=400, details="No file part")

    file = request.files['file']

    if file.filename == '':
        current_app.logger.error("File name is empty")
        return custom_response(status_code=400, details="File name is empty")

    if file:
        file_type = file.filename.split(".")[-1]

        if file_type != "gcode":
            current_app.logger.error(f"File type {file_type} not allowed")
            return custom_response(status_code=400, details="File type not allowed")
        return upload_file_with_catches(file, "gcode")
    else:
        current_app.logger.error("No file in the request")
        return custom_response(status_code=400, details="No file in the request")


def upload_file_with_catches(file, directory_name):
    try:
        uploader = GoogleDriveUploader()
        file_slug, folder_slug = uploader.upload_file(file, directory_name)
    except Exception as e:
        current_app.logger.error(f"An error occurred while uploading the file: {e}")
        return custom_response(status_code=500, details="An error occurred while uploading the file.")

    current_app.logger.info(f"File uploaded successfully - File Slug: {file_slug}, Folder Slug: {folder_slug}")
    data = {
        "file_slug": file_slug,
        "folder_slug": folder_slug
    }
    return custom_response(status_code=200, details=data)
