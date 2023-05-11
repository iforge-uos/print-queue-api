import os
from flask import Blueprint, request, current_app
from print_api.common.routing import custom_response
from print_api.common.gdrive import GoogleDriveUploader


file_upload_api = Blueprint("file_upload", __name__)

file_upload_path = os.getenv("UPLOAD_FOLDER")


@file_upload_api.route("/upload_stl", methods=["POST"])
def upload_stl():
    """
    API Route to upload an STL file to the server
    """
    logger = current_app.logger

    if 'file' not in request.files:
        logger.error("No file part in the request")
        return custom_response(status_code=400, details="No file part")

    file = request.files['file']

    if file.filename == '':
        logger.error("File name is empty")
        return custom_response(status_code=400, details="File name is empty")

    if file:
        file_type = file.filename.split(".")[-1]

        if file_type not in ["stl", "3mf", "obj"]:
            logger.error(f"File type {file_type} not allowed")
            return custom_response(status_code=400, details="File type not allowed")

        return upload_file_with_catches(file, "stls")
    else:
        logger.error("No file in the request")
        return custom_response(status_code=400, details="No file in the request")


@file_upload_api.route("/upload_gcode", methods=["POST"])
def upload_gcode():
    """
    API Route to upload an STL file to the server
    """
    logger = current_app.logger

    if 'file' not in request.files:
        logger.error("No file part in the request")
        return custom_response(status_code=400, details="No file part")

    file = request.files['file']

    if file.filename == '':
        logger.error("File name is empty")
        return custom_response(status_code=400, details="File name is empty")

    if file:
        file_type = file.filename.split(".")[-1]

        if file_type != "gcode":
            logger.error(f"File type {file_type} not allowed")
            return custom_response(status_code=400, details="File type not allowed")
        return upload_file_with_catches(file, "gcode")
    else:
        logger.error("No file in the request")
        return custom_response(status_code=400, details="No file in the request")


def upload_file_with_catches(file, directory_name):
    logger = current_app.logger
    try:
        uploader = GoogleDriveUploader()
        file_slug, folder_slug = uploader.upload_file(file, directory_name)
    except Exception as e:
        logger.error(f"An error occurred while uploading the file: {e}")
        return custom_response(status_code=500, details="An error occurred while uploading the file.")

    logger.info(f"File uploaded successfully - File Slug: {file_slug}, Folder Slug: {folder_slug}")
    data = {
        "file_slug": file_slug,
        "folder_slug": folder_slug
    }
    return custom_response(status_code=200, details=data)
