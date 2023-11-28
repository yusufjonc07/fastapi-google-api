from fastapi import FastAPI
from google_drive.drive import drive_router

app = FastAPI(title='FastAPI & Google Integration examples')

app.include_router(drive_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)