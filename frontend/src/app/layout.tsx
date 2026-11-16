import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'MediRAG | AI Knowledge Workspace', description: 'Multi-domain RAG platform frontend prototype' };
export default function RootLayout({children}: {children: React.ReactNode}) {return <html lang="en"><body>{children}</body></html>}
