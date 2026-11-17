'use client';
import {PanelLeftClose, Plus, Search} from 'lucide-react';
import type {ChatBot} from '../types';

type Props = {
  title: string;
  bots: ChatBot[];
  botId: string;
  onBotChange: (id: string) => void;
  busy: boolean;
  onToggleHistory: () => void;
  onNew: () => void;
  webSearch: boolean;
  onWebSearchChange: (value: boolean) => void;
};

export function ChatHeader(p: Props) {
  return <>
    <div className="v3-chat-top">
      <button className="outline v3-icon" type="button" title="Toggle chat history" aria-label="Toggle chat history" onClick={p.onToggleHistory}><PanelLeftClose size={18}/></button>
      <div className="v3-chat-title"><strong>{p.title}</strong><small>Grounded answers from your trusted knowledge</small></div>
      <button type="button" className="secondary" disabled={p.busy} onClick={p.onNew}><Plus size={15}/> New chat</button>
    </div>
    <div className="v3-chat-settings">
      <label>Assistant <select value={p.botId} onChange={e => p.onBotChange(e.target.value)}>{p.bots.map(b => <option value={b.id} key={b.id}>{b.name}</option>)}</select></label>
      <label className="v3-web"><input type="checkbox" checked={p.webSearch} disabled={p.busy} onChange={e => p.onWebSearchChange(e.target.checked)}/><Search size={14}/> Web search (optional)</label>
    </div>
  </>;
}
