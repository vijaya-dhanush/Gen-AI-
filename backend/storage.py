import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import MAX_CONVERSATION_MESSAGES

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "conversations"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _conversation_file(conversation_id: str) -> Path:
    return DATA_DIR / f"{conversation_id}.json"


def list_conversations() -> list[dict]:
    summaries = []
    for file in DATA_DIR.glob("*.json"):
        try:
            payload = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        summaries.append(
            {
                "id": payload.get("id", file.stem),
                "created_at": payload.get("created_at"),
                "message_count": len(payload.get("messages", [])),
            }
        )
    summaries.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return summaries


def create_conversation() -> dict:
    conversation_id = str(uuid4())
    payload = {"id": conversation_id, "created_at": _now_iso(), "messages": []}
    save_conversation(payload)
    return payload


def get_conversation(conversation_id: str) -> dict | None:
    file = _conversation_file(conversation_id)
    if not file.exists():
        return None
    return json.loads(file.read_text(encoding="utf-8"))


def save_conversation(conversation: dict) -> None:
    file = _conversation_file(conversation["id"])
    file.write_text(json.dumps(conversation, indent=2), encoding="utf-8")


def append_message(conversation_id: str, message: dict) -> dict | None:
    conversation = get_conversation(conversation_id)
    if not conversation:
        return None

    messages = conversation.setdefault("messages", [])
    messages.append(message)
    if len(messages) > MAX_CONVERSATION_MESSAGES:
        conversation["messages"] = messages[-MAX_CONVERSATION_MESSAGES:]

    save_conversation(conversation)
    return conversation
