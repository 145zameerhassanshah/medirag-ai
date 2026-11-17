"""Document ingestion and deletion."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company, owned_kb, out
from app.db.session import DB
from app.db.models import User, Company, KB, Document, Product, Bot, Conversation, Message
from app.schemas.inputs import Register, Login, UserProfileIn, CompanyIn, KBIn, BotIn, ProductIn, ConversationUpdate, ChatIn
import os
from pathlib import Path
from fastapi import Form, File, UploadFile
from app.db.base import sid
from app.rag.store import add_texts, collection
from app.rag.ingestion import extract

router = APIRouter()

@router.get('/api/companies/{company_id}/documents')
def list_documents(company_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    return [out(d,['id','kb_id','filename','chunks','created_at']) for d in db.scalars(select(Document).where(Document.company_id==company_id))]
@router.post('/api/companies/{company_id}/documents',status_code=201)
async def upload_document(company_id:str,user:UserDep,db:DB,kb_id:str=Form(...),file:UploadFile=File(...)):
    owned_company(db,user,company_id);owned_kb(db,company_id,kb_id)
    name=Path(file.filename or '').name
    if not name or Path(name).suffix.lower() not in ('.pdf','.docx','.txt','.md'):raise HTTPException(415,'Unsupported file extension')
    max_bytes=int(os.getenv('MAX_UPLOAD_MB','15'))*1024*1024
    data=await file.read(max_bytes+1)
    if len(data)>max_bytes:raise HTTPException(413,'File too large')
    try:pages=extract(name,data)
    except HTTPException:raise
    except Exception:raise HTTPException(422,'Document could not be parsed')
    if not any(p[2].strip() for p in pages):raise HTTPException(422,'No extractable text; scanned PDFs require OCR')
    did=sid();directory=Path(os.getenv('UPLOAD_DIR','./storage/uploads'))/company_id/kb_id;directory.mkdir(parents=True,exist_ok=True)
    location=directory/(did+Path(name).suffix.lower());location.write_bytes(data)
    try:count=add_texts(company_id,kb_id,did,name,pages)
    except Exception:
        location.unlink(missing_ok=True)
        # remove any partial batches if indexing failed
        try:collection(company_id,kb_id).delete(where={'document_id':did})
        except Exception:pass
        raise HTTPException(503,'Indexing failed; check embedding model and ChromaDB configuration')
    d=Document(id=did,company_id=company_id,kb_id=kb_id,filename=name,storage_path=str(location),chunks=count)
    db.add(d);db.commit()
    return out(d,['id','kb_id','filename','chunks'])
@router.delete('/api/companies/{company_id}/documents/{document_id}')
def delete_document(company_id:str,document_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    d=db.get(Document,document_id)
    if not d or d.company_id!=company_id:raise HTTPException(404,'Document not found')
    collection(company_id,d.kb_id).delete(where={'document_id':d.id})
    Path(d.storage_path).unlink(missing_ok=True)
    db.delete(d);db.commit();return {'deleted':True}
