"""Provider adapter with actual token metadata when available (never guess token counts)."""
from dataclasses import dataclass
import os
from functools import lru_cache

@dataclass
class AIResult:
    text: str
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

@lru_cache(maxsize=2)
def _gemini_client(api_key: str, timeout_ms: int):
    from google import genai
    from google.genai import types
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=timeout_ms))

@lru_cache(maxsize=2)
def _openai_client(api_key: str, timeout_s: float):
    from openai import OpenAI
    return OpenAI(api_key=api_key, timeout=timeout_s, max_retries=0)

def generate(*, instructions: str, input_text: str, max_output_tokens: int = 420):
    provider = os.getenv('LLM_PROVIDER','none').strip().lower()
    if provider == 'gemini':
        key=os.getenv('GEMINI_API_KEY','')
        if not key: raise RuntimeError('GEMINI_API_KEY missing')
        from google.genai import types
        model=os.getenv('GEMINI_MODEL','gemini-3.1-flash-lite')
        client=_gemini_client(key, max(2000,int(os.getenv('MEDIRAG_MODEL_TIMEOUT_S','30'))*1000))
        response=client.models.generate_content(
            model=model,
            contents=input_text,
            config=types.GenerateContentConfig(
                system_instruction=instructions, temperature=0.2,
                max_output_tokens=max_output_tokens,
            ),
        )
        usage=getattr(response,'usage_metadata',None)
        return AIResult((response.text or '').strip(),provider,model,
                        getattr(usage,'prompt_token_count',None),
                        getattr(usage,'candidates_token_count',None),
                        getattr(usage,'total_token_count',None))
    if provider == 'openai':
        key=os.getenv('OPENAI_API_KEY','')
        if not key: raise RuntimeError('OPENAI_API_KEY missing')
        model=os.getenv('OPENAI_MODEL','gpt-5.5')
        response=_openai_client(key, max(2.0,float(os.getenv('MEDIRAG_MODEL_TIMEOUT_S','30')))).responses.create(
            model=model,
            instructions=instructions,
            input=input_text,
            max_output_tokens=max_output_tokens,
        )
        usage=getattr(response,'usage',None)
        return AIResult((response.output_text or '').strip(),provider,model,
                        getattr(usage,'input_tokens',None),
                        getattr(usage,'output_tokens',None),
                        getattr(usage,'total_tokens',None))
    raise RuntimeError('Configure LLM_PROVIDER=gemini or openai and a valid key')

def model_answer(prompt: str) -> str:
    """Legacy compatibility for imports outside Stage 3 chat flow."""
    return generate(instructions='Answer clearly and accurately.',input_text=prompt,max_output_tokens=850).text
