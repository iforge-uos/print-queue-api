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
    # TODO MAKE THIS .ENV
    gauth = GoogleAuth()
    scope = ["https://www.googleapis.com/auth/drive"]
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        '../../iforge-print-queue-5908fc90eea8_secret.json', scope)
    drive = GoogleDrive(gauth)

    # TODO make this .ENV
    f = drive.CreateFile({
        'title': os.path.basename(file_path),
        'parents': [{
            'kind': 'drive#fileLink',
            'teamDriveId': '0ACBtghjfnl3UUk9PVA',
            'id': '1epWmYouqcg_l25Zr8H9U6CLngohTcsZ8'
        }]
    })
    f.SetContentFile(file_path)

    f.Upload(param={'supportsTeamDrives': True})
    f.content.close()
    os.remove(file_path)
    return f['id']

