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

    def create_folder(self, folder_name, parent_folder_id):
        query = f"mimeType='application/vnd.google-apps.folder' and trashed = false and name='{folder_name}' and '{parent_folder_id}' in parents"

        results = self.drive_service.files().list(q=query, supportsAllDrives=True,
                                                  includeItemsFromAllDrives=True).execute()
        items = results.get('files', [])

        if not items:
            # If the folder does not exist, create it
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            folder = self.drive_service.files().create(body=folder_metadata, supportsAllDrives=True,
                                                       fields='id').execute()
            return folder['id']
        else:
            # If the folder already exists, return its ID
            return items[0]['id']

    def upload_file(self, file, subfolder_name):
        parent_folder_id = os.getenv('DRIVE_PARENT_FOLDER_ID')

        # Create a subfolder inside the parent folder, or get its ID if it already exists
        subfolder_id = self.create_folder(subfolder_name, parent_folder_id)

        # Create a BytesIO buffer and write the file data to it
        buffer = BytesIO()
        buffer.write(file.read())
        buffer.seek(0)

        # Create a MediaIoBaseUpload object with the buffer
        media = MediaIoBaseUpload(buffer, mimetype=file.content_type)

        request = self.drive_service.files().create(
            body={
                'name': file.filename,
                'parents': [subfolder_id]
            },
            media_body=media,
            fields='id',
            supportsAllDrives=True
        )

        response = None
        try:
            response = request.execute()
        except Exception as e:
            print(f"An error occurred: {e}")

        file_id = response['id'] if response else None

        return file_id, subfolder_id
