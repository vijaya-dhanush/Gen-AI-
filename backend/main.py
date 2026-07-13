from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .council import (
    calculate_aggregate_rankings,
    stage1_collect_responses,
    stage2_collect_rankings,
    stage3_synthesize_final,
)
from .models import MessageCreateRequest
from .storage import (
    append_message,
    create_conversation,
    get_conversation,
    list_conversations,
)

app = FastAPI(title="LLM Council API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/conversations")
async def conversations_list() -> dict:
    return {"conversations": list_conversations()}


@app.post("/api/conversations")
async def conversations_create() -> dict:
    conversation = create_conversation()
    return conversation


@app.get("/api/conversations/{conversation_id}")
async def conversations_get(conversation_id: str) -> dict:
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post("/api/conversations/{conversation_id}/message")
async def conversations_message(conversation_id: str, request: MessageCreateRequest) -> dict:
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_message = {"role": "user", "content": request.content, "created_at": _now_iso()}
    append_message(conversation_id, user_message)

    stage1 = await stage1_collect_responses(request.content)
    stage2, label_to_model = await stage2_collect_rankings(stage1, request.content)
    aggregate_rankings = calculate_aggregate_rankings(stage2, label_to_model)
    stage3 = await stage3_synthesize_final(request.content, stage1, stage2)

    assistant_message = {
        "role": "assistant",
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3,
        "created_at": _now_iso(),
    }
    updated = append_message(conversation_id, assistant_message)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to save conversation")

    return {
        "conversation": updated,
        "metadata": {
            "label_to_model": label_to_model,
            "aggregate_rankings": aggregate_rankings,
        },
    }


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=False)
