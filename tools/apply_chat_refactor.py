"""Safely extract only the Live Chat JSX block from the current MediRAG V3 page.
Run from project root: python path/to/apply_chat_refactor.py
"""
from pathlib import Path
import sys

root = Path.cwd()
page = root / 'frontend' / 'src' / 'app' / 'live' / 'page.tsx'
if not page.is_file():
    sys.exit(f'ERROR: Run from project root, cannot find {page}')

old = page.read_text(encoding='utf-8')
marker_start = " {tab==='Live Chat'&&<section className=\"card v3-chat-card\">"
marker_end = " {tab==='History'&&<section className=\"card\">"
if "import {LiveChatPanel}" in old:
    sys.exit('Already patched; no changes made.')
if old.count(marker_start) != 1 or old.count(marker_end) != 1:
    sys.exit('ERROR: V3 chat block markers missing or duplicated. No changes made. Your local page may differ; manual review needed.')

start, end = old.index(marker_start), old.index(marker_end)
if end <= start:
    sys.exit('ERROR: Invalid block order; no changes made.')

new_block = """ {tab==='Live Chat'&&<LiveChatPanel
    historyOpen={historyOpen} setHistoryOpen={setHistoryOpen}
    chatSearch={chatSearch} setChatSearch={setChatSearch}
    hist={hist} conversationId={conversationId} messages={messages}
    bots={bots} botId={botId} busy={busy} chatStatus={chatStatus}
    question={question} setQuestion={setQuestion}
    webSearch={webSearch} setWebSearch={setWebSearch}
    chatBottom={chatBottom}
    onSend={()=>void chat()}
    onNew={()=>{setConversationId('');setMessages([]);setQuestion('')}}
    onBotChange={id=>{setBotId(id);setConversationId('');setMessages([])}}
    onOpen={(id,selectedBotId)=>void openConversation(id,selectedBotId)}
    onRename={(id,title)=>void renameChat(id,title)}
    onDelete={(id,title)=>void deleteChat(id,title)}
 />}
"""
import_line = "import {LiveChatPanel} from '../../features/chat/LiveChatPanel';\n"
anchor = "import remarkGfm from 'remark-gfm';\n"
if old.count(anchor) != 1:
    sys.exit('ERROR: Expected React Markdown import not found; no changes made.')
new = old[:start] + new_block + old[end:]
new = new.replace(anchor, anchor + import_line, 1)
backup = page.with_name('page.pre_modular_chat.tsx.backup')
if backup.exists():
    sys.exit(f'ERROR: Backup already exists at {backup}; move it to a safe location before rerunning.')
backup.write_text(old, encoding='utf-8')
page.write_text(new, encoding='utf-8')
print('SUCCESS: Extracted Live Chat UI into reusable components.')
print('Backup:', backup)
print('Updated:', page)
print('Other tabs/components were not modified.')
