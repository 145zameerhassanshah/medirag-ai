'use client';
import React, {useCallback,useEffect,useState} from 'react';
import Link from 'next/link';
import {Bot,ArrowLeft,Save,Activity,ShieldCheck} from 'lucide-react';

type Company={id:string;name:string};
type Assistant={id:string;name:string};
type Policy={role:string;language:string;tone:string;answer_length:string;allow_general:boolean;
  require_citations:boolean;max_output_tokens:number;prompt_version:string;company_instructions:string};
type Usage={requests:number;llm_calls:number;known_input_tokens:number;known_output_tokens:number;
  unknown_token_events:number;average_ms:number;routes:Record<string,number>};
const API=process.env.NEXT_PUBLIC_RAG_API_BASE_URL||'http://127.0.0.1:8000';
const defaultPolicy:Policy={role:'knowledge',language:'auto',tone:'friendly',answer_length:'adaptive',
  allow_general:false,require_citations:true,max_output_tokens:420,prompt_version:'p3',company_instructions:''};

export default function AssistantSettings(){
 const [token,setToken]=useState('');
 const [companies,setCompanies]=useState<Company[]>([]),[company,setCompany]=useState('');
 const [bots,setBots]=useState<Assistant[]>([]),[bot,setBot]=useState('');
 const [policy,setPolicy]=useState<Policy>(defaultPolicy),[usage,setUsage]=useState<Usage|null>(null);
 const [busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
 useEffect(()=>{setToken(sessionStorage.getItem('medirag_access')||'')},[]);
 const api=useCallback(async(path:string,method='GET',body?:unknown)=>{
   const res=await fetch(API+path,{method,headers:{Authorization:`Bearer ${token}`,
    ...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined});
   const data=await res.json(); if(!res.ok)throw Error(typeof data.detail==='string'?data.detail:`Request failed: ${res.status}`);
   return data;
 },[token]);
 useEffect(()=>{if(!token)return;api('/api/companies').then((list:Company[])=>{setCompanies(list);setCompany(list[0]?.id||'')}).catch(e=>setError(e.message))},[token,api]);
 useEffect(()=>{if(!company)return;setBot('');setBots([]);Promise.all([
   api(`/api/companies/${company}/bots`),api(`/api/companies/${company}/usage/summary`)
 ]).then(([b,u]:[Assistant[],Usage])=>{setBots(b);setBot(b[0]?.id||'');setUsage(u)}).catch(e=>setError(e.message))},[company,api]);
 useEffect(()=>{if(!company||!bot)return;api(`/api/companies/${company}/bots/${bot}/response-policy`)
   .then(setPolicy).catch(e=>setError(e.message))},[company,bot,api]);
 const set=<K extends keyof Policy>(key:K,value:Policy[K])=>setPolicy(p=>({...p,[key]:value}));
 const save=async()=>{setBusy(true);setError('');setNotice('');try{await api(`/api/companies/${company}/bots/${bot}/response-policy`,'PUT',policy);
    setNotice('Assistant policy saved. New messages will use these settings.');}
    catch(e){setError(e instanceof Error?e.message:'Failed to save')}finally{setBusy(false)}};
 const inputStyle:React.CSSProperties={width:'100%',padding:'11px 12px',border:'1px solid #d7dfe7',borderRadius:10,
  background:'white',color:'#14233b',fontSize:14};
 const card:React.CSSProperties={background:'#fff',padding:24,borderRadius:16,border:'1px solid #e5eaf0',marginBottom:16};
 const field=(label:string,child:React.ReactNode)=><label style={{display:'grid',gap:7,fontSize:13,fontWeight:600,color:'#293b55'}}>{label}{child}</label>;
 if(!token)return <main style={{maxWidth:650,margin:'70px auto',padding:22}}><h1>Assistant settings</h1><p>Sign in to MediRAG first.</p><Link href="/live">Go to Login</Link></main>;
 return <main style={{minHeight:'100vh',background:'#f5f7fb',padding:'38px 20px',color:'#14233b'}}>
  <div style={{maxWidth:960,margin:'auto'}}>
   <Link href="/live" style={{display:'inline-flex',gap:8,alignItems:'center',marginBottom:22,color:'#435c7a'}}><ArrowLeft size={16}/> Back to workspace</Link>
   <h1 style={{display:'flex',alignItems:'center',gap:10,fontSize:28,marginBottom:8}}><Bot/> AI Assistant Settings</h1>
   <p style={{color:'#61758b',marginBottom:24}}>Configure bot role, answer style, general knowledge and prompt version. Platform security rules remain enforced.</p>
   {error&&<div role="alert" style={{...card,borderColor:'#e99',color:'#9e2929'}}>{error}</div>}
   {notice&&<div role="status" style={{...card,borderColor:'#b9dcc6'}}>{notice}</div>}
   <section style={card}>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:18}}>
     {field('Company',<select style={inputStyle} value={company} onChange={e=>setCompany(e.target.value)}>{companies.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select>)}
     {field('Assistant',<select style={inputStyle} value={bot} onChange={e=>setBot(e.target.value)}>{bots.map(b=><option key={b.id} value={b.id}>{b.name}</option>)}</select>)}
    </div>
   </section>
   {bot&&<section style={card}>
    <h2 style={{fontSize:19,marginBottom:20}}>Response configuration</h2>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:18}}>
    {field('Assistant role',<select style={inputStyle} value={policy.role} onChange={e=>set('role',e.target.value)}>
      <option value="knowledge">Knowledge Q&A</option><option value="medical_education">Medical Education</option>
      <option value="sales">Sales & Product</option><option value="support">Customer Support</option>
      <option value="content">Content Generator</option></select>)}
    {field('Tone',<select style={inputStyle} value={policy.tone} onChange={e=>set('tone',e.target.value)}>
      <option>friendly</option><option>professional</option><option>concise</option></select>)}
    {field('Language',<select style={inputStyle} value={policy.language} onChange={e=>set('language',e.target.value)}>
      <option value="auto">Match customer</option><option value="english">English</option>
      <option value="urdu">Urdu</option><option value="roman_urdu">Roman Urdu</option></select>)}
    {field('Answer detail',<select style={inputStyle} value={policy.answer_length} onChange={e=>set('answer_length',e.target.value)}>
      <option value="adaptive">Adaptive</option><option value="short">Short</option>
      <option value="detailed">Detailed</option></select>)}
    {field('Prompt version',<select style={inputStyle} value={policy.prompt_version} onChange={e=>set('prompt_version',e.target.value)}>
      <option value="p1">P1 — Baseline</option><option value="p2">P2 — Concise</option>
      <option value="p3">P3 — Grounded</option><option value="p4">P4 — Guided</option></select>)}
    {field('Max output tokens',<input style={inputStyle} type="number" min={120} max={1000} value={policy.max_output_tokens}
      onChange={e=>set('max_output_tokens',Number(e.target.value))}/>)}
    </div>
    <div style={{display:'grid',gap:14,marginTop:24,marginBottom:20}}>
      <label><input type="checkbox" checked={policy.allow_general} onChange={e=>set('allow_general',e.target.checked)}/> Allow general educational AI replies (when no verified company answer exists)</label>
      <label><input type="checkbox" checked={policy.require_citations} onChange={e=>set('require_citations',e.target.checked)}/> Require citations for document-grounded answers</label>
      <p style={{color:'#687b92',fontSize:13,margin:0}}>Disabling citations changes answer display, not source requirements. Company-specific assertions still require evidence.</p>
    </div>
    {field('Additional company style notes (never override platform rules)',<textarea style={{...inputStyle,minHeight:100}} maxLength={1400} value={policy.company_instructions} onChange={e=>set('company_instructions',e.target.value)}/>)}
    <button disabled={busy} type="button" onClick={()=>void save()} style={{display:'flex',alignItems:'center',gap:8,marginTop:20,background:'#245bda',color:'white',padding:'12px 20px',border:0,borderRadius:10,cursor:'pointer'}}><Save size={16}/>{busy?'Saving...':'Save Assistant Settings'}</button>
   </section>}
   <section style={card}>
    <h2 style={{display:'flex',alignItems:'center',gap:8,fontSize:19}}><Activity size={20}/> Company AI Usage</h2>
    {usage?<div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(130px,1fr))',gap:16,marginTop:15}}>
      {[['Requests',usage.requests],['LLM calls',usage.llm_calls],['Input tokens',usage.known_input_tokens],
        ['Output tokens',usage.known_output_tokens],['Unknown token events',usage.unknown_token_events],
        ['Average latency (ms)',usage.average_ms]].map(([k,v])=><div key={k} style={{background:'#f5f7fb',padding:14,borderRadius:10}}><div style={{fontSize:23,fontWeight:700}}>{v}</div><div style={{fontSize:12,color:'#64768b'}}>{k}</div></div>)}
    </div>:<p>No usage data loaded.</p>}
    <p style={{display:'flex',gap:7,alignItems:'center',fontSize:12,color:'#697b90',marginTop:18}}><ShieldCheck size={15}/> Token numbers are provider-reported when available; unknown usage is not treated as zero.</p>
   </section>
  </div>
 </main>;
}
