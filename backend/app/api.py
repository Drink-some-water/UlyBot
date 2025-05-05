from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from models import MP3File
from database import Base, engine, SessionLocal

app = FastAPI()
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
        files = db.query(File).all()
        
        # Return a list of filenames
        return {"files": [file.filename for file in files]}
    
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
