import io
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile

"""
Wrapper class for oauth2client library in google-api-python-client
"""
gauth = GoogleAuth()

"""
API Router which has to be included app in main.py file
"""
drive_router = APIRouter(tags=["GOOGLE DRIVE EXAMPLES"])

"""
connect to the google with downloaded credentials client id
authentification flow will be available after app runs
"""    
@drive_router.on_event("startup")
async def connect_google():
    gauth.LocalWebserverAuth()

"""
simple example of getting list of files on the google drive
"""
@drive_router.get("/files")
async def list_of_files():
    drive = GoogleDrive(gauth)

    """
    title and id of the file are loaded and appended to the empty list
    """
    filel_ist = [{"id": file['id'], "filename": file['title']} for file in drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()]
    
    """return the list of fileNames and fileIds"""
    return filel_ist

"""
simple example of uploading file 
using FastAPI UploadFile to the Google Drive
"""
@drive_router.post('/upload_file')
async def upload_file_to_drive(
   file: UploadFile = File(...)
):
    drive = GoogleDrive(gauth)
    """Creating new file and uploading it"""
    file1 = drive.CreateFile({'title': file.filename})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    
    """we use the io bytes so that the content of the file will be flexible for google file content"""
    file_content = io.BytesIO(await file.read())
    file1.content = file_content # Set content of the file
    
    """ Main function which uploads the filled file to the Drive """
    file1.Upload()
    
    """ Make user aware of the success """
    return 'success'


"""
In this route, you can download the file 
using its ID which was taken in the GET request above
"""
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
