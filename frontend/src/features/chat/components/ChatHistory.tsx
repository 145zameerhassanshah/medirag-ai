'use client';
import {MessageCircle, Pencil, Plus, Trash2} from 'lucide-react';
import type {ConversationSummary} from '../types';

type Props = {
  open: boolean;
  search: string;
  onSearchChange: (value: string) => void;
  conversations: ConversationSummary[];
  currentId: string;
  busy: boolean;
  onNew: () => void;
  onOpen: (id: string, botId: string) => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string, title: string) => void;
};

export function ChatHistory(p: Props) {
  const filtered = p.conversations.filter(x => x.title.toLowerCase().includes(p.search.toLowerCase()));
  return <aside className={'v3-chat-history ' + (p.open ? 'is-open' : '')} aria-label="Conversation history">
    <div className="v3-history-head">
      <strong>Chats</strong>
      <button type="button" className="outline v3-icon" title="New conversation" disabled={p.busy} onClick={p.onNew}><Plus size={17}/></button>
    </div>
    <input className="v3-history-search" aria-label="Search chat titles" value={p.search} onChange={e => p.onSearchChange(e.target.value)} placeholder="Search conversations"/>
    <div className="v3-history-list">
      {filtered.map(h => <div key={h.id} className={'v3-history-item ' + (p.currentId === h.id ? 'selected' : '')}>
        <button type="button" className="v3-history-open" disabled={p.busy} onClick={() => p.onOpen(h.id, h.bot_id)} title={h.title}><MessageCircle size={15}/><span>{h.title}</span></button>
        <button type="button" title="Rename" aria-label={'Rename ' + h.title} className="v3-history-action" disabled={p.busy} onClick={() => p.onRename(h.id, h.title)}><Pencil size={14}/></button>
        <button type="button" title="Delete" aria-label={'Delete ' + h.title} className="v3-history-action" disabled={p.busy} onClick={() => p.onDelete(h.id, h.title)}><Trash2 size={14}/></button>
      </div>)}
      {filtered.length === 0 && <p className="muted tiny" style={{padding: 14}}>No matching conversations yet.</p>}
    </div>
  </aside>;
}
