"""Import basic Anki text exports (tab-separated front/back; HTML is preserved)."""
def parse_anki_text(text: str) -> list[dict[str, str]]:
    cards = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) < 2 or not fields[0].strip() or not fields[1].strip():
            raise ValueError("Anki text export rows must contain tab-separated front and back")
        fmt = "cloze" if "{{c" in fields[0] else "markdown"
        cards.append({"front": fields[0].strip(), "back": fields[1].strip(), "format": fmt})
    if not cards:
        raise ValueError("No Anki text rows found")
    return cards
