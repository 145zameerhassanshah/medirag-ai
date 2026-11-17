'use client';
import {memo} from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {SourceCitations} from './SourceCitations';
import type {ChatMessage} from '../types';

const safeUrl = (url: string) => {
  try {
    const parsed = new URL(url);
    return ['https:', 'http:', 'mailto:'].includes(parsed.protocol) ? url : '';
  } catch { return ''; }
};

function MessageBubbleBase({message, assistantName}: {message: ChatMessage; assistantName: string}) {
  const copy = async () => {
    try { await navigator.clipboard.writeText(message.content); }
    catch { /* Clipboard permissions may be blocked in insecure contexts. */ }
  };
  return <div className={'bubble ' + message.role}>
    <b>{message.role === 'user' ? 'You' : assistantName}</b>
    <div className="chat-markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml urlTransform={safeUrl}>{message.content}</ReactMarkdown></div>
    <div className="chat-tools"><button type="button" onClick={() => void copy()}>Copy {message.role === 'user' ? 'message' : 'answer'}</button></div>
    <SourceCitations sources={message.citations || []}/>
  </div>;
}

export const MessageBubble = memo(MessageBubbleBase);
