import {memo} from 'react';
import {BookOpen} from 'lucide-react';
import type {Citation} from '../types';

function SourceCitationsBase({sources}: {sources: Citation[]}) {
  if (!sources.length) return null;
  return <details>
    <summary className="source-summary"><BookOpen size={14}/> View {sources.length} supporting source{sources.length === 1 ? '' : 's'}</summary>
    {sources.map((c, j) => <div className="source" key={c.source_id + '-' + j}>
      <strong>[{c.source_id}] {c.filename}</strong> · {c.type === 'web' ? 'External website' : c.page_start != null ? `PDF page ${c.page_start}` : 'Page unavailable'} {c.section && `· ${c.section}`}
      {c.url && <p><a href={c.url} target="_blank" rel="noopener noreferrer">Open external page</a></p>}
      <p>{c.excerpt}</p>
    </div>)}
  </details>;
}

export const SourceCitations = memo(SourceCitationsBase);
