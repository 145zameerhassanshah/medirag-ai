import type {RefObject} from 'react';
import {MessageCircle} from 'lucide-react';
import {MessageBubble} from './MessageBubble';
import type {ChatMessage} from '../types';

type Props = {
  messages: ChatMessage[];
  assistantName: string;
  greeting: string;
  busy: boolean;
  status: string;
  bottomRef: RefObject<HTMLDivElement | null>;
};

export function MessageList(p: Props) {
  return <div className="chat v3-chat-messages" aria-live="polite" aria-busy={p.busy}>
    {!p.messages.length && <div className="chat-welcome"><span className="chat-welcome-icon"><MessageCircle size={26}/></span><h3>{p.greeting}</h3><p>Ask about your documents, clinical recommendations or company knowledge.</p></div>}
    {p.messages.map((m, i) => <MessageBubble key={m.id || i} message={m} assistantName={p.assistantName}/>)}
    {p.busy && <div className="v3-thinking" role="status"><span className="v3-spinner"/> {p.status || 'Preparing your response…'}</div>}
    <div ref={p.bottomRef}/>
  </div>;
}
