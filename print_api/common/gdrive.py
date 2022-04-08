import os
from pydrive.auth import GoogleAuth, ServiceAccountCredentials
from pydrive.drive import GoogleDrive


def upload_file(file_path: str) -> str:
    """
    Takes a file path, uploads the file to the google drive and then deletes the local copy returning the file slug.
    The slug is the unique identifier for the file in the google drive.
    :param file_path: The path to the file to upload.
    :return: The slug of the file in the google drive.
    """
    gauth = GoogleAuth()
    scope = ["https://www.googleapis.com/auth/drive"]
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        f"../../{os.getenv('DRIVE_CREDENTIALS_FILENAME')}", scope)

    drive = GoogleDrive(gauth)

    f = drive.CreateFile({
        'title': os.path.basename(file_path),
        'parents': [{
            'kind': 'drive#fileLink',
            'teamDriveId': os.getenv('DRIVE_TEAM_DRIVE_ID'),
            'id': os.getenv('DRIVE_PARENT_FOLDER_ID')
        }]
    })

    f.SetContentFile(file_path)
    f.Upload(param={'supportsTeamDrives': True})
    f.content.close()

    os.remove(file_path)
    return f['id']
