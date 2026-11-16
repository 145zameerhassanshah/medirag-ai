"""Read-only MediRAG retrieval quality experiment.

Place beside backend/main.py. Run from backend/ with its existing virtualenv.
No LLM calls, database writes, or re-indexing.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="MediRAG retrieval experiment (read only)")
    parser.add_argument("--company-id", help="Company UUID; optional if only one is in DB")
    parser.add_argument("--kb-id", help="Knowledgebase UUID; optional if only one matches")
    parser.add_argument("--document-id", help="Optional metadata filter for one indexed document")
    parser.add_argument("--out", default="retrieval_eval", help="Folder for CSV outputs")
    args = parser.parse_args()

    import main as api  # Uses exact same SQLite/Chroma/embedding config as backend
    from sqlalchemy import select

    with api.SessionLocal() as db:
        companies = db.scalars(select(api.Company)).all()
        company = next((c for c in companies if c.id == args.company_id), None) if args.company_id else (companies[0] if len(companies) == 1 else None)
        if company is None:
            print("Available companies:")
            for c in companies:
                print(f"  {c.id}  {c.name}")
            raise SystemExit("Choose --company-id from the list above (do not guess).")
        kbs = db.scalars(select(api.KB).where(api.KB.company_id == company.id)).all()
        kb = next((k for k in kbs if k.id == args.kb_id), None) if args.kb_id else (kbs[0] if len(kbs) == 1 else None)
        if kb is None:
            print(f"Knowledgebases in {company.name}:")
            for k in kbs:
                print(f"  {k.id}  {k.name}")
            raise SystemExit("Choose --kb-id from the list above.")
        documents = db.scalars(select(api.Document).where(api.Document.company_id == company.id, api.Document.kb_id == kb.id)).all()
        print(f"Company: {company.name} [{company.id}]")
        print(f"Knowledgebase: {kb.name} [{kb.id}]")
        print("Indexed document records:")
        for doc in documents:
            print(f"  {doc.id} | {doc.filename} | recorded chunks={doc.chunks}")

    col = api.collection(company.id, kb.id)
    total = col.count()
    print(f"Actual vector chunks: {total}")
    if total == 0:
        raise SystemExit("STOP: vector collection is empty for this KB. Verify uploaded docs / correct organization before evaluating.")

    if args.document_id:
        # Require the selected document to belong to the chosen company+KB.
        if args.document_id not in {d.id for d in documents}:
            raise SystemExit("Document ID is not a PDF/document record in this company + KB.")
        filters = {"document_id": args.document_id}
        eligible = len(col.get(where=filters, include=[])["ids"])
        if not eligible:
            raise SystemExit("Document metadata filter matched zero Chroma records.")
    else:
        filters = None
        eligible = total

    questions = [
        ("Q01", "What does WHO recommend about starting antihypertensive medication?", "relevant"),
        ("Q02", "When should adults with hypertension begin pharmacological treatment?", "relevant"),
        ("Q03", "How often should patients be followed up after starting treatment?", "relevant"),
        ("Q04", "What blood pressure target is recommended for adults with cardiovascular disease?", "relevant"),
        ("Q05", "What are recommended first-line antihypertensive drug classes?", "relevant"),
        ("Q06", "What does this guideline say about monitoring after treatment initiation?", "relevant"),
        ("Q07", "Who won the 2018 FIFA World Cup?", "out_of_scope"),
        ("Q08", "What is the price of an iPhone?", "out_of_scope"),
    ]
    top_ks = [3, 5, 10]
    thresholds = [0.30, 0.45, 0.60]
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    details = []
    summary = []

    for qid, question, category in questions:
        tick = time.perf_counter()
        query_vector = api.embed([question])
        embed_ms = round((time.perf_counter() - tick) * 1000, 2)
        tick = time.perf_counter()
        result = col.query(
            query_embeddings=query_vector,
            n_results=min(max(top_ks), eligible),
            where=filters,
            include=["documents", "metadatas", "distances"],
        )
        retrieval_ms = round((time.perf_counter() - tick) * 1000, 2)
        hits = []
        for rid, txt, meta, dist in zip(result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]):
            hits.append({"chunk_id": rid, "text": txt, "metadata": meta, "score": 1 - float(dist)})
        for k in top_ks:
            for threshold in thresholds:
                accepted = [h for h in hits[:k] if h["score"] >= threshold]
                summary.append({
                    "question_id": qid, "question": question, "category": category,
                    "top_k": k, "threshold": threshold, "retrieved": min(k, len(hits)),
                    "accepted": len(accepted), "max_score": round(hits[0]["score"], 4) if hits else "",
                    "embedding_ms": embed_ms, "retrieval_ms": retrieval_ms,
                    "any_passed": int(bool(accepted)),
                })
                for rank, h in enumerate(hits[:k], 1):
                    meta = h["metadata"]
                    details.append({
                        "question_id": qid, "category": category, "question": question,
                        "top_k": k, "threshold": threshold, "rank": rank,
                        "accepted": int(h["score"] >= threshold),
                        "similarity": round(h["score"], 4), "chunk_id": h["chunk_id"],
                        "document_id": meta.get("document_id", ""),
                        "filename": meta.get("filename", ""),
                        "page": meta.get("page", ""), "section": meta.get("section", ""),
                        "passage": h["text"],
                        "human_relevant_0_or_1": "",  # MUST label manually; do not pretend automated relevance.
                    })
        print(f"{qid} {category:12} best similarity={hits[0]['score']:.3f}" if hits else f"{qid} no hits")

    for name, rows in [("retrieval_details.csv", details), ("retrieval_summary.csv", summary)]:
        with (output / name).open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        print(f"Saved {output / name}")

    with (output / "experiment_info.json").open("w", encoding="utf-8") as f:
        json.dump({"company_id": company.id, "kb_id": kb.id, "document_id": args.document_id,
                   "vector_chunks": total, "top_ks": top_ks, "thresholds": thresholds,
                   "note": "Manual relevance labels are required to compute Precision@K, Recall@K, or MRR. No LLM calls."}, f, indent=2)
    print("Label human_relevant_0_or_1 after checking source passages against the PDF.")
    print("WARNING: accepted count is NOT precision or accuracy; out-of-scope queries should ideally have zero accepted chunks.")


if __name__ == "__main__":
    main()
