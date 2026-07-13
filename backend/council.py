from statistics import mean

from .config import CHAIRMAN_MODEL, COUNCIL_MODELS
from .openrouter import query_model, query_models_parallel


def _label(index: int) -> str:
    return f"Response {chr(ord('A') + index)}"


def parse_ranking_from_text(text: str) -> list[str]:
    if not text:
        return []

    upper_text = text.upper()
    marker = "FINAL RANKING:"
    ranking_part = text
    marker_idx = upper_text.find(marker)
    if marker_idx >= 0:
        ranking_part = text[marker_idx + len(marker) :]

    extracted: list[str] = []
    for raw_line in ranking_part.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ". " in line:
            _, line = line.split(". ", 1)

        normalized = line.upper().strip()
        if normalized.startswith("RESPONSE ") and len(normalized) >= len("RESPONSE A"):
            suffix = normalized[len("RESPONSE ") :].strip()
            if not suffix:
                continue
            label_char = suffix[0]
            if not ("A" <= label_char <= "Z"):
                continue
            label = f"Response {label_char}"
            if label not in extracted:
                extracted.append(label)

    return extracted


async def stage1_collect_responses(user_prompt: str) -> list[dict]:
    system_prompt = "You are a council member. Give a clear, concise answer to the user question."
    return await query_models_parallel(COUNCIL_MODELS, user_prompt, system_prompt=system_prompt)


async def stage2_collect_rankings(stage1_responses: list[dict], user_prompt: str) -> tuple[list[dict], dict[str, str]]:
    labeled = []
    label_to_model: dict[str, str] = {}
    for idx, response in enumerate(stage1_responses):
        label = _label(idx)
        labeled.append((label, response))
        label_to_model[label] = response["model"]

    blocks = [f"{label}:\n{response['content']}" for label, response in labeled]
    responses_text = "\n\n".join(blocks)

    prompt = (
        "You are reviewing anonymous responses from multiple models.\n"
        f"Original user question:\n{user_prompt}\n\n"
        "Responses:\n"
        f"{responses_text}\n\n"
        "Instructions:\n"
        "1. Evaluate each response individually for accuracy, clarity, and insight.\n"
        "2. Then provide your final ordering from best to worst.\n"
        "3. Use this exact format at the end:\n"
        "FINAL RANKING:\n"
        "1. Response X\n2. Response Y\n...\n"
        "4. Do not include any text after the ranked list."
    )

    rankings: list[dict] = []
    for model in COUNCIL_MODELS:
        result = await query_model(model, prompt)
        if not result:
            continue
        raw_text = result.get("content", "")
        parsed = parse_ranking_from_text(raw_text)
        rankings.append(
            {
                "model": model,
                "raw_evaluation": raw_text,
                "parsed_ranking": parsed,
            }
        )

    return rankings, label_to_model


def calculate_aggregate_rankings(rankings: list[dict], label_to_model: dict[str, str]) -> list[dict]:
    positions: dict[str, list[int]] = {label: [] for label in label_to_model.keys()}

    for ranking in rankings:
        parsed = ranking.get("parsed_ranking", [])
        for position, label in enumerate(parsed, start=1):
            if label in positions:
                positions[label].append(position)

    aggregate = []
    for label, model in label_to_model.items():
        votes = positions.get(label, [])
        if votes:
            aggregate.append(
                {
                    "label": label,
                    "model": model,
                    "average_position": round(mean(votes), 2),
                    "vote_count": len(votes),
                }
            )

    aggregate.sort(key=lambda item: item["average_position"])
    return aggregate


async def stage3_synthesize_final(user_prompt: str, stage1_responses: list[dict], stage2_rankings: list[dict]) -> str:
    if not stage1_responses:
        return "No stage 1 responses were available."

    stage1_text = "\n\n".join([f"{r['model']}:\n{r['content']}" for r in stage1_responses])
    stage2_text = "\n\n".join(
        [f"{r['model']} ranking:\n{r.get('raw_evaluation', '')}" for r in stage2_rankings]
    )

    prompt = (
        "You are the chairman of an LLM council.\n"
        "Given the user's question, first-pass responses, and peer rankings, create the best final answer.\n"
        "Focus on correctness, clarity, and practical usefulness.\n\n"
        f"User question:\n{user_prompt}\n\n"
        f"Stage 1 responses:\n{stage1_text}\n\n"
        f"Stage 2 peer evaluations:\n{stage2_text}"
    )

    final = await query_model(CHAIRMAN_MODEL, prompt)
    if not final or not final.get("content"):
        return "Failed to synthesize a final response."
    return final["content"]
