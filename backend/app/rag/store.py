"""Embedding and Chroma collection management; retains original collection names."""
import hashlib, os, re
from pathlib import Path
from fastapi import HTTPException

# Lazy-load large ML dependencies only when ingestion/chat occurs.
_chroma=None
_model=None
def chroma():
    global _chroma
    if _chroma is None:
        import chromadb
        _chroma=chromadb.PersistentClient(path=os.getenv('CHROMA_DIR','./storage/chroma'))
    return _chroma

def embed(texts:list[str]):
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model=SentenceTransformer(os.getenv('EMBEDDING_MODEL','sentence-transformers/all-MiniLM-L6-v2'))
    return _model.encode(texts,normalize_embeddings=True,show_progress_bar=False).tolist()

def collection(company_id:str,kb_id:str):
    key=hashlib.sha256(f'{company_id}:{kb_id}'.encode()).hexdigest()[:40]
    return chroma().get_or_create_collection(name='kb_'+key,metadata={'hnsw:space':'cosine'})

def add_texts(company_id,kb_id,document_id,filename,items):
    # items=(page,section,text). Metadata is backend-derived, not LLM-generated.
    records=[]
    for page,section,text in items:
        text=re.sub(r'\s+',' ',text).strip()
        # character chunker, overlap 160
        start=0
        while start<len(text):
            stop=min(start+1000,len(text));part=text[start:stop].strip()
            if part:records.append((page,section,part))
            if stop==len(text):break
            start=max(start+1,stop-160)
    if not records:return 0
    col=collection(company_id,kb_id)
    for batch_start in range(0,len(records),48):
        batch=records[batch_start:batch_start+48]
        vectors=embed([x[2] for x in batch])
        col.add(ids=[f'{document_id}_{batch_start+i}' for i in range(len(batch))], embeddings=vectors,documents=[x[2] for x in batch],metadatas=[{'document_id':document_id,'filename':filename,'page':p,'section':s,'company_id':company_id,'kb_id':kb_id} for p,s,_ in batch])
    return len(records)
