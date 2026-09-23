"""Convert Anki-style {{c1::answer::hint}} deletions into cloze card sides."""
import re
PATTERN = re.compile(r"\{\{c(\d+)::(.*?)(?:::(.*?))?\}\}")

def parse_cloze(text: str) -> list[dict[str, str]]:
    cards = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        matches = list(PATTERN.finditer(line))
        if not matches:
            raise ValueError("Each non-empty line must contain {{cN::answer}} cloze syntax")
        ids = sorted({int(m.group(1)) for m in matches})
        for cid in ids:
            front = PATTERN.sub(lambda m: "[…]" if int(m.group(1)) == cid else m.group(2), line)
            answers = [m.group(2) + (f" (hint: {m.group(3)})" if m.group(3) else "") for m in matches if int(m.group(1)) == cid]
            cards.append({"front": front, "back": "; ".join(answers), "format": "cloze"})
    if not cards:
        raise ValueError("No cloze cards found")
    return cards
