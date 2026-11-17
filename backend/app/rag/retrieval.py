"""Tenant-scoped vector retrieval; source locations are backend-controlled."""
import hashlib
import os
import re
from app.rag.store import collection, embed
from app.rag.prompts import is_title_only

STOP = {'what','about','does','the','for','and','with','when','who','how','are','is','was',
        'to','from','can','patients','patient','recommend','recommendation','guideline','guidelines'}

def terms(text):
    raw = re.sub(r'[^a-z0-9 ]', ' ', text.casefold()).split()
    return set('diabetes' if w in {'diabetic', 'diabetes'} else
               'hypertension' if w in {'hypertension','hypertensive','htn'} else w
               for w in raw if w not in STOP and len(w)>3)

def retrieve(*, company_id, kb_id, question, followup_query=None, top_k=5, threshold=None):
    col = collection(company_id, kb_id)
    if not col.count():
        return [], []
    size = min(col.count(), max(top_k * 3, 12))
    queries = [question]
    if followup_query and followup_query != question:
        queries.append(followup_query)
    candidates = {}
    for query_text in queries:
        result = col.query(query_embeddings=embed([query_text]), n_results=size,
                           include=['documents','metadatas','distances'])
        for chunk_id, text, meta, distance in zip(result['ids'][0],result['documents'][0],
                                                  result['metadatas'][0],result['distances'][0]):
            meta = meta or {}
            # Double-check metadata, never rely on collection name alone.
            if meta.get('company_id') != company_id or meta.get('kb_id') != kb_id:
                continue
            score = 1 - float(distance)
            if is_title_only(text):
                continue
            if chunk_id not in candidates or score > candidates[chunk_id]['similarity']:
                candidates[chunk_id] = {'id':chunk_id,'text':text,'meta':meta,'similarity':score}
    keywords = terms(question)
    for candidate in candidates.values():
        paragraph = candidate['text'].casefold()
        overlap = len(keywords & terms(paragraph)) / max(len(keywords), 1)
        clinical = bool(re.search(r'\b(who recommends|who suggests|recommendation on|blood pressure threshold|treatment goal)\b',paragraph))
        noise = bool(re.search(r'\b(contributors|acknowledgements|references|cost.effectiveness study|harvard|director|biography)\b',paragraph))
        candidate['rerank_score'] = candidate['similarity']*0.62 + overlap*0.26 + (0.10 if clinical else 0) - (0.13 if noise else 0)
    ranked = sorted(candidates.values(),key=lambda c:c['rerank_score'],reverse=True)
    cutoff = threshold if threshold is not None else float(os.getenv('MIN_SIMILARITY','0.45'))
    citations=[]; evidence=[];used=set()
    for item in ranked:
        text, meta, score = item['text'],item['meta'],item['similarity']
        if score < cutoff:continue
        fingerprint=hashlib.sha256(text.strip().casefold().encode()).hexdigest()
        if fingerprint in used:continue
        used.add(fingerprint)
        sid = f'S{len(citations)+1}'
        citations.append({'source_id':sid,'document_id':meta.get('document_id'),
                          'filename':meta.get('filename','Document'),'page_start':meta.get('page') or None,
                          'section':meta.get('section',''),'score':round(score,4),
                          'excerpt':text[:240],'type':'document'})
        evidence.append(f'[{sid}] DOCUMENT: {meta.get("filename","Document")} | page {meta.get("page") or "N/A"} | section {meta.get("section", "")}\n{text[:850]}')
        if len(citations)>=min(top_k,4):break
    return citations,evidence
