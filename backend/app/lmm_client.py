from fastapi import HTTPException
from huggingface_hub import InferenceClient
from app.dependencies import settings 

_client: InferenceClient | None = None

def get_hf_client() -> InferenceClient:
    global _client
    if _client is None:
        _client = InferenceClient(
            provider=settings.hf_provider,
            api_key=settings.hf_api_token,
        )
    return _client

def ask_llm(prompt: str) -> str:
    client = get_hf_client()
    try:
        completion = client.chat.completions.create(
            model=settings.hf_model_name,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM inference error: {e}")

    if (
        hasattr(completion, "choices")
        and len(completion.choices) > 0
        and hasattr(completion.choices[0], "message")
    ):
        return completion.choices[0].message.content

    raise HTTPException(
        status_code=502,
        detail="LLM did not return a valid completion structure"
    )
