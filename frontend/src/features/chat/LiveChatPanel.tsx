'use client';
import type {RefObject} from 'react';
import {ChatHistory} from './components/ChatHistory';
import {ChatHeader} from './components/ChatHeader';
import {MessageList} from './components/MessageList';
import {ChatComposer} from './components/ChatComposer';
import type {ChatBot, ChatMessage, ConversationSummary} from './types';

export type LiveChatProps = {
  historyOpen: boolean;
  setHistoryOpen: (next: (prev: boolean) => boolean) => void;
  chatSearch: string;
  setChatSearch: (value: string) => void;
  hist: ConversationSummary[];
  conversationId: string;
  messages: ChatMessage[];
  bots: ChatBot[];
  botId: string;
  busy: boolean;
  chatStatus: string;
  question: string;
  setQuestion: (value: string) => void;
  webSearch: boolean;
  setWebSearch: (value: boolean) => void;
  chatBottom: RefObject<HTMLDivElement | null>;
  onSend: () => void;
  onNew: () => void;
  onBotChange: (id: string) => void;
  onOpen: (id: string, botId: string) => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string, title: string) => void;
};

export function LiveChatPanel(p: LiveChatProps) {
  const currentBot = p.bots.find(b => b.id === p.botId);
  return <section className="card v3-chat-card">
    <div className="v3-chat-layout">
      <ChatHistory open={p.historyOpen} search={p.chatSearch} onSearchChange={p.setChatSearch}
        conversations={p.hist} currentId={p.conversationId} busy={p.busy}
        onNew={p.onNew} onOpen={p.onOpen} onRename={p.onRename} onDelete={p.onDelete}/>
      <div className="v3-chat-main">
        <ChatHeader title={p.hist.find(h => h.id === p.conversationId)?.title || 'New conversation'}
          bots={p.bots} botId={p.botId} onBotChange={p.onBotChange} busy={p.busy}
          onToggleHistory={() => p.setHistoryOpen(x => !x)} onNew={p.onNew}
          webSearch={p.webSearch} onWebSearchChange={p.setWebSearch}/>
        <MessageList messages={p.messages} assistantName={currentBot?.name || 'Assistant'} greeting={currentBot?.greeting || 'Hello! How can I help?'} busy={p.busy} status={p.chatStatus} bottomRef={p.chatBottom}/>
        <ChatComposer value={p.question} onChange={p.setQuestion} onSend={p.onSend} busy={p.busy} enabled={!!p.botId}/>
      </div>
    </div>
  </section>;
}
