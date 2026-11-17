"""Response helpers. Prompt construction remains in chat route pending Stage 2."""
import re

# SOURCE-ONLY DEFAULT. Real web search is opt-in and requires a separate provider key.
FALLBACK = ("I couldn't find enough reliable information in this organization's "
            "knowledgebase to answer that. Try asking about an uploaded document "
            "or selecting a different assistant.")

def courtesy_reply(question: str, greeting: str) -> str | None:
    q = re.sub(r"[!?.\s]+$", "", question.casefold().strip())
    if q in {"hi", "hello", "hey", "hey there", "hello there", "salam", "assalamualaikum", "assalam o alaikum", "اسلام علیکم", "سلام"}:
        return greeting.strip() or "Hello! How can I help you with your documents today?"
    if q in {"thanks", "thank you", "thankyou", "shukriya", "شکریہ"}:
        return "You're welcome! What else can I help you with?"
    if q in {"bye", "goodbye", "allah hafiz"}:
        return "Goodbye! Feel free to return whenever you have a question."
    return None

def is_title_only(text: str) -> bool:
    norm = re.sub(r'\s+', ' ', text).strip()
    return len(norm) < 115 or norm.casefold() == 'guideline for the pharmacological treatment of hypertension in adults'
