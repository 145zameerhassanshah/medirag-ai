'use client';
import {Send} from 'lucide-react';

type Props = {value: string; onChange: (text: string) => void; onSend: () => void; busy: boolean; enabled: boolean};
export function ChatComposer(p: Props) {
  return <>
    <form className="v3-composer" onSubmit={e => { e.preventDefault(); if (!p.busy && p.enabled && p.value.trim()) p.onSend(); }}>
      <textarea rows={2} placeholder="Message your assistant…" value={p.value} maxLength={2000}
        onChange={e => p.onChange(e.target.value)}
        onKeyDown={e => {if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {e.preventDefault(); if (!p.busy && p.enabled && p.value.trim()) p.onSend();}}}/>
      <button type="submit" disabled={p.busy || !p.enabled || !p.value.trim()} aria-label="Send message">
        {p.busy ? <span className="v3-spinner"/> : <Send size={18}/>}
      </button>
    </form>
    <p className="muted tiny v3-disclaimer">Enter to send · Shift+Enter for new line · Review medical decisions against original clinical guidance.</p>
  </>;
}
