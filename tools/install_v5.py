#!/usr/bin/env python3
"""MediRAG performance stage 5: inspect by default, --apply to patch. No DB changes."""
from __future__ import annotations
import argparse, datetime, pathlib, shutil, sys, re

PATCH_FILES=['backend/app/services/chat_service.py', 'backend/app/rag/providers.py', 'backend/app/api/routes/chat.py', 'frontend/src/features/chat/components/MessageBubble.tsx', 'frontend/src/features/chat/components/SourceCitations.tsx', 'backend/tests/test_performance_v5.py']
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT
p=argparse.ArgumentParser()
p.add_argument('--project',type=pathlib.Path,default=pathlib.Path.cwd(),help='Your medirag_fullstack root')
p.add_argument('--apply',action='store_true')
a=p.parse_args()
project=a.project.resolve()
required=['backend/app/services/chat_service.py','backend/app/rag/providers.py','backend/app/api/routes/chat.py',
          'frontend/src/app/live/page.tsx']
missing=[x for x in required if not (project/x).is_file()]
if missing:sys.exit('Missing existing files (install Stage 1/3/V4 first): '+', '.join(missing))
old=(project/'backend/app/services/chat_service.py').read_text(encoding='utf-8')
if 'resolve_context' not in old or 'load_policy' not in old:
    sys.exit('V4 + Stage3 code expected; refusing to overwrite different backend.')
if 'authorization_ms=_ms(start)' in old:
    sys.exit('Stage 5 seems already applied; no changes made.')
page=project/'frontend/src/app/live/page.tsx'
text=page.read_text(encoding='utf-8')
if 'await fetchCompany();' not in text:
    sys.exit('Expected chat refresh not found in page.tsx; refusing unsafe patch.')
# Limit to chat() function, not other awaited refreshes such as organization editing.
start=text.find(' const chat=async()=>{')
if start<0:start=text.find('const chat=async()=>{')
end=text.find(' const openConversation=',start)
if end<0:end=text.find('const openConversation=',start)
if start<0 or end<start:sys.exit('Could not locate chat function safely; no files changed.')
block=text[start:end]
if block.count('await fetchCompany();')!=1:
    sys.exit('Unexpected chat refresh count; no files changed.')
block=block.replace('await fetchCompany();',
    "// Refresh history without keeping the chat spinner active.\n     void fetchCompany().catch(e=>console.warn('History refresh failed',e));")
# Neutral status avoids reporting retrieval for an approved FAQ or Yes follow-up.
block=re.sub(r"setChatStatus\(webSearch\?'Searching the web and preparing an answer…':'Retrieving sources and preparing your answer…'\);",
    "setChatStatus('Preparing your answer…');",block)
block=block.replace("setChatStatus('Retrieving sources and preparing your answer…')", "setChatStatus('Preparing your answer…')")
block=block.replace("setChatStatus('Preparing your answer…');\n     setConversationId", "setChatStatus('Answer ready');\n     setConversationId")
modified=text[:start]+block+text[end:]
# Smooth scrolling on each busy state causes unnecessary work when messages are long.
modified=modified.replace("chatBottom.current?.scrollIntoView({behavior:'smooth',block:'end'})", "chatBottom.current?.scrollIntoView({behavior:'auto',block:'end'})")
print('Project:',project)
print('Will install 3 backend files + 2 memoized chat components')
print('Will patch only chat() refresh/loading in frontend/src/app/live/page.tsx')
print('Will not touch .env, SQLite, Chroma, documents, or unrelated frontend screens')
if not a.apply:
    print('DRY RUN ONLY. Add --apply to install.')
    sys.exit(0)
backup=pathlib.Path.home()/('MediRAG-V5-Backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True,exist_ok=True)
paths=list(PATCH_FILES)
paths.append('frontend/src/app/live/page.tsx')
for rel in paths:
    target=project/rel
    if target.exists():
        saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(target,saved)
for rel in PATCH_FILES:
    src=SOURCE/rel; dst=project/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
page.write_text(modified,encoding='utf-8')
print('Installed. Backup:',backup)
print('Next: cd backend && python -m pytest tests/test_performance_v5.py -q')
