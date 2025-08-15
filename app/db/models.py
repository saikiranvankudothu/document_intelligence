from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_path = Column(String, nullable=True)
    text = Column(Text)  # cleaned full text
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    title = Column(String, nullable=True)
    level = Column(Integer, default=1)       # 1,2,3,...
    start_line = Column(Integer, default=0)
    end_line = Column(Integer, default=0)
    content = Column(Text)                   # section text
    parent_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    document = relationship("Document", back_populates="sections")
    children = relationship("Section", cascade="all, delete-orphan")
