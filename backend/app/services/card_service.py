import re
from datetime import datetime, timezone


CARD_COUNT = 3
CARD_METHOD = "mock"
CARD_QUESTIONS = (
    "What is the core topic of this material?",
    "Which key idea should you review from this material?",
    "How would you explain this material in one sentence?",
)


def _card_source_text(material: dict) -> str:
    for field in ("ai_summary", "text_preview", "summary"):
        text = material.get(field, "")
        if text and text.strip():
            return text.strip()

    return ""


def _text_fragments(text: str) -> list[str]:
    fragments = [
        fragment.strip()
        for fragment in re.split(r"(?<=[.!?])\s+", text)
        if fragment.strip()
    ]
    return fragments or [text]


def generate_mock_cards(material: dict) -> dict:
    text = _card_source_text(material)
    if not text:
        raise ValueError("Material has no text available for card generation")

    fragments = _text_fragments(text)
    created_at = datetime.now(timezone.utc).isoformat()
    cards = []
    for index in range(CARD_COUNT):
        cards.append(
            {
                "id": material["id"] * 100 + index + 1,
                "question": CARD_QUESTIONS[index],
                "answer": fragments[index % len(fragments)][:240],
                "source_material_id": material["id"],
                "card_type": "concept" if index == 0 else "review",
                "created_at": created_at,
            }
        )

    return {
        "cards": cards,
        "cards_generated": True,
        "cards_generated_at": created_at,
        "cards_method": CARD_METHOD,
    }