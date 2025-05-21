from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.models import MP3File
from app.database import Base, engine, SessionLocal
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
@app.get("/get-files")
def get_files(db: Session = Depends(get_db)):
    try:
        # Fetch all files from the database
        files = db.query(MP3File).all()
        
        # Return a list of filenames
        

        return {
            "files": [
                {
                    "filename": file.filename,
                    "content": base64.b64encode(file.content).decode('utf-8')
                }
                for file in files
            ]
        }

    
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload/")
async def upload_mp3(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".mp3"):
        return {"error": "Only MP3 files are allowed."}

    content = await file.read()

    mp3_entry = MP3File(filename=file.filename, content=content)
    db.add(mp3_entry)
    db.commit()
    db.refresh(mp3_entry)

    return {"message": "Upload successful", "id": mp3_entry.id}
