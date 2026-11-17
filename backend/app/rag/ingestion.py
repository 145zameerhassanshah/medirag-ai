"""PDF, DOCX and text extraction; no database or LLM calls."""
from pathlib import Path
from fastapi import HTTPException

def extract(filename:str,content:bytes):
    ext=Path(filename).suffix.lower()
    if ext=='.pdf':
        import fitz
        pdf=fitz.open(stream=content,filetype='pdf')
        try:
            output=[]
            for i,page in enumerate(pdf):
                txt=page.get_text('text')
                headings=[]
                for block in page.get_text('dict').get('blocks',[]):
                    for line in block.get('lines',[]):
                        spans=line.get('spans',[])
                        label=' '.join(span.get('text','').strip() for span in spans).strip()
                        if label and len(label)<100 and any(span.get('size',0)>=14 for span in spans):
                            headings.append((max(span.get('size',0) for span in spans),label))
                section=max(headings,key=lambda x:x[0])[1] if headings else f'Page {i+1} (heading unavailable)'
                output.append((i+1,section,txt))
            return output
        finally:pdf.close()
    if ext=='.docx':
        from docx import Document as WordDocument
        from io import BytesIO
        doc=WordDocument(BytesIO(content))
        sections=[];heading='Document'
        for p in doc.paragraphs:
            if p.style and p.style.name.startswith('Heading'):heading=p.text.strip() or heading
            elif p.text.strip():sections.append((0,heading,p.text.strip()))
        return sections
    if ext in ('.txt','.md'):
        return [(0,'Document',content.decode('utf-8-sig',errors='replace'))]
    raise HTTPException(415,'Supported formats: PDF, DOCX, TXT, MD')
