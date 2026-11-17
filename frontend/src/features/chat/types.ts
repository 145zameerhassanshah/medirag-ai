export type Citation = {
  source_id: string;
  filename: string;
  page_start: number | null;
  section: string;
  score: number | null;
  excerpt: string;
  url?: string;
  type?: string;
};

export type ChatMessage = {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
};

export type ConversationSummary = {
  id: string;
  title: string;
  bot_id: string;
};

export type ChatBot = {
  id: string;
  name: string;
  kb_id: string;
  tone: string;
  greeting: string;
};
