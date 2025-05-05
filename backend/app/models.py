from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base

class MP3File(Base):
    __tablename__ = "mp3files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    content = Column(LargeBinary)
