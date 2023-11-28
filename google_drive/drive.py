import io
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile

# Authenticate with Google
gauth = GoogleAuth()

# Create an APIRouter for Google Drive operations
drive_router = APIRouter(tags=["GOOGLE DRIVE EXAMPLES"])

# Event to connect to Google Drive on application startup
@drive_router.on_event("startup")
async def connect_google():
    gauth.LocalWebserverAuth()

# Endpoint to list files in Google Drive
@drive_router.get("/files")
async def list_of_files():
    drive = GoogleDrive(gauth)
    # Retrieve a list of files in the root directory (not trashed)
    file_list = [{"id": file['id'], "filename": file['title']} for file in drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()]
    return file_list

# Endpoint to upload a file to Google Drive
@drive_router.post('/upload_file')
async def upload_file_to_drive(file: UploadFile = File(...)):
    drive = GoogleDrive(gauth)
    file1 = drive.CreateFile({'title': file.filename})
    file_content = io.BytesIO(await file.read())
    file1.content = file_content
    file1.Upload()
    return 'success'

# Endpoint to download a file from Google Drive
@drive_router.get('/download_file')
async def download_file_from_drive(fileId: str):
    drive = GoogleDrive(gauth)
    file1 = drive.CreateFile({'id': fileId})
    file1.FetchMetadata()
    # Save the file content to a temporary file
    with NamedTemporaryFile(delete=False) as temp_file:
        file1.GetContentFile(temp_file.name)
    # Return the temporary file as a response
    return FileResponse(temp_file.name, filename=file1['title'])

# Endpoint to delete a file from Google Drive
@drive_router.delete('/delete_file')
async def delete_file_in_drive(fileId: str):
    try:
        drive = GoogleDrive(gauth)
        file1 = drive.CreateFile({'id': fileId})
        file1.FetchMetadata()
        file1.Delete()
        return 'success'
    except ApiRequestError as e:
        print(e)
        return e
