from io import BytesIO
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


class GoogleDriveUploader:
    def __init__(self):
        self.credentials = self._get_credentials()
        self.drive_service = self._get_drive_service()

    @staticmethod
    def _get_credentials():
        return Credentials.from_service_account_file(
            f"{os.getenv('DRIVE_CREDENTIALS_FILENAME')}",
            scopes=["https://www.googleapis.com/auth/drive"]
        )

    def _get_drive_service(self):
        return build('drive', 'v3', credentials=self.credentials)

    def upload_file(self, file):
        # Create a BytesIO buffer and write the file data to it
        buffer = BytesIO()
        buffer.write(file.read())
        buffer.seek(0)

        # Create a MediaIoBaseUpload object with the buffer
        media = MediaIoBaseUpload(buffer, mimetype=file.content_type)

        request = self.drive_service.files().create(
            body={
                'name': file.filename,
                'parents': [os.getenv('DRIVE_PARENT_FOLDER_ID')]
            },
            media_body=media,
            fields='id',
            supportsTeamDrives=True
        )

        response = None
        try:
            response = request.execute()
        except Exception as e:
            print(f"An error occurred: {e}")

        return response['id'] if response else None
