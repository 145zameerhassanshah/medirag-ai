"""Compute deterministic comparison metrics from saved candidate outputs.
Input JSONL: {"question_id":"Q1","version":"p3","answer":"...","allowed_citations":["S1"],
              "latency_ms":1000,"input_tokens":123,"output_tokens":42,"human_accuracy":2,"human_faithfulness":2}
Manual correctness scores are OPTIONAL and must be supplied by a human reviewer.
"""
import csv,json,re,sys
from collections import defaultdict
from pathlib import Path

def summarize(entries):
    grouped=defaultdict(list)
    for row in entries:grouped[row['version']].append(row)
    results=[]
    for version,rows in sorted(grouped.items()):
        refs=[(set(re.findall(r'\[(S\d+)\]',r['answer'])),set(r.get('allowed_citations',[]))) for r in rows]
        results.append({
            'version':version,'questions':len(rows),
            'invalid_citation_answers':sum(bool(used-allowed) for used,allowed in refs),
            'mean_answer_words':round(sum(len(r['answer'].split()) for r in rows)/len(rows),1),
            'mean_latency_ms':round(sum(r.get('latency_ms',0) for r in rows)/len(rows),1),
            'known_input_tokens':sum(r.get('input_tokens') or 0 for r in rows),
            'known_output_tokens':sum(r.get('output_tokens') or 0 for r in rows),
            'human_accuracy_mean':round(sum(r['human_accuracy'] for r in rows if r.get('human_accuracy') is not None)/sum(r.get('human_accuracy') is not None for r in rows),2) if any(r.get('human_accuracy') is not None for r in rows) else 'NOT_SCORED',
            'human_faithfulness_mean':round(sum(r['human_faithfulness'] for r in rows if r.get('human_faithfulness') is not None)/sum(r.get('human_faithfulness') is not None for r in rows),2) if any(r.get('human_faithfulness') is not None for r in rows) else 'NOT_SCORED',
        })
    return results

def main():
    if len(sys.argv)!=3:raise SystemExit('Usage: python evaluation/compare_prompts.py saved_outputs.jsonl comparison.csv')
    entries=[json.loads(line) for line in Path(sys.argv[1]).read_text(encoding='utf-8').splitlines() if line.strip()]
    if not entries:raise SystemExit('No rows in input')
    report=summarize(entries)
    with open(sys.argv[2],'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(report[0]));writer.writeheader();writer.writerows(report)
    print('Saved',sys.argv[2]);print(*report,sep='\n')
if __name__=='__main__':main()
