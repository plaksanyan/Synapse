"""Parse plain cards separated by blank lines; each block uses front :: back."""
def parse_txt(text: str) -> list[dict[str, str]]:
    cards = []
    for block in text.replace("\r\n", "\n").split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if "\t" in block:
            front, back = block.split("\t", 1)
        elif "::" in block:
            front, back = block.split("::", 1)
        else:
            lines = block.splitlines()
            if len(lines) != 2:
                raise ValueError("Each card must have front and back separated by a tab or ::")
            front, back = lines
        front, back = front.strip(), back.strip()
        if not front or not back:
            raise ValueError("Card front and back cannot be empty")
        cards.append({"front": front, "back": back, "format": "text"})
    if not cards:
        raise ValueError("No cards found")
    return cards
