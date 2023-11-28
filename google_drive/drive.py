import io
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile

gauth = GoogleAuth()

drive_router = APIRouter(tags=["GOOGLE DRIVE EXAMPLES"])
    
@drive_router.on_event("startup")
async def connect_google():
    gauth.LocalWebserverAuth()


@drive_router.get("/files")
async def list_of_files():
    drive = GoogleDrive(gauth)
    filel_ist = [{"id": file['id'], "filename": file['title']} for file in drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()]
    return filel_ist

@drive_router.post('/upload_file')
async def upload_file_to_drive(
   file: UploadFile = File(...)
):
    drive = GoogleDrive(gauth)
    # Creating new file and uploading it
    file1 = drive.CreateFile({'title': file.filename})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    file_content = io.BytesIO(await file.read())
    file1.content = file_content # Set content of the file from given string.
    file1.Upload()
    
    return 'success'


@drive_router.get('/download_file')
async def download_file_from_drive(
   fileId: str
):

    drive = GoogleDrive(gauth)

    file1 = drive.CreateFile({'id': fileId})
    file1.FetchMetadata() 
    with NamedTemporaryFile(delete=False) as temp_file:
        file1.GetContentFile(temp_file.name)
        
    return FileResponse(temp_file.name, filename=file1['title'])
        
    

@drive_router.delete('/delete_file')
async def delete_file_in_drive(
   fileId: str
):
    try:
        drive = GoogleDrive(gauth)

        file1 = drive.CreateFile({'id': fileId})  # 
        file1.FetchMetadata()
        file1.Delete()
        
        return 'success'
    except ApiRequestError as e:
        print(e)
        return e
