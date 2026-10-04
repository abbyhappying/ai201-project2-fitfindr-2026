"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    query_words = _keywords(description)
    if not query_words:
        return []

    wanted_size = _size_tokens(size) if size else None

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if wanted_size and not wanted_size <= _size_tokens(listing["size"]):
            continue

        score = _score(query_words, listing)
        if score > 0:
            scored.append((score, listing))

    # sorted() is stable, so equal scores keep their order in the data.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "with", "in", "of", "to", "on",
    "my", "me", "i", "some", "something", "looking", "want", "need",
}


def _normalize(word: str) -> str:
    """Lowercase and drop a plural 's' so 'tees' matches 'tee'."""
    word = word.lower()
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return word


def _keywords(text: str) -> set[str]:
    """Split free text into normalized keywords, minus filler words."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {_normalize(w) for w in words if w not in _STOPWORDS}


def _size_tokens(size: str) -> set[str]:
    """
    Break a size string into whole tokens: "S/M" → {"s", "m"},
    "W30 L30" → {"w30", "l30"}, "US 8.5" → {"us", "8.5"}.

    Matching on whole tokens instead of substrings is what stops "S" from
    matching "US 9" and "L" from matching "XL".
    """
    return set(re.findall(r"[a-z0-9.]+", size.lower()))


def _score(query_words: set[str], listing: dict) -> int:
    """
    Count query keywords that appear in the listing. Title, style tags and
    category count double, because a hit there is what the item *is*; a hit
    in the description or colors counts once.
    """
    strong = _keywords(
        " ".join([listing["title"], listing["category"], *listing["style_tags"]])
    )
    weak = _keywords(
        " ".join([listing["description"], *listing["colors"], listing["brand"] or ""])
    )
    return sum(2 if w in strong else 1 if w in weak else 0 for w in query_words)


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []
    item_text = _describe_item(new_item)

    if not items:
        prompt = (
            f"Someone is thinking about buying this thrifted piece:\n{item_text}\n\n"
            "They haven't told you what's in their wardrobe. Suggest one or two "
            "outfits built around this piece using common basics most people "
            "own (plain tees, jeans, simple sneakers, and so on). Start by "
            "saying in one short sentence that these are general ideas since "
            "their wardrobe is empty."
        )
    else:
        wardrobe_text = "\n".join(_describe_wardrobe_item(w) for w in items)
        prompt = (
            f"Someone is thinking about buying this thrifted piece:\n{item_text}\n\n"
            f"This is what they already own:\n{wardrobe_text}\n\n"
            "Suggest one or two outfits that pair the new piece with specific "
            "items from their wardrobe. Name each wardrobe piece exactly as "
            "listed above. Only use pieces from that list."
        )

    response = generate(prompt, system=_OUTFIT_SYSTEM)

    # The model can come back blank. The loop needs a non-empty string, so
    # fall back to a plain suggestion instead of passing "" along.
    if not response.strip():
        return (
            f"No specific outfit came back for the {new_item.get('title', 'item')}. "
            "As a starting point, pair it with simple basics in neutral colors "
            "and let the piece be the focus."
        )
    return response


_OUTFIT_SYSTEM = (
    "You are a friendly personal stylist for thrift shoppers. Keep answers "
    "short: one or two outfits, each a few lines. Be concrete about which "
    "pieces go together and why. Don't invent details about the item that "
    "aren't in its listing."
)


def _describe_item(item: dict) -> str:
    """One listing as a few labelled lines. Skips brand when there isn't one."""
    lines = [
        f"- Title: {item.get('title', '')}",
        f"- Category: {item.get('category', '')}",
        f"- Colors: {', '.join(item.get('colors') or [])}",
        f"- Style: {', '.join(item.get('style_tags') or [])}",
        f"- Size: {item.get('size', '')}",
        f"- Description: {item.get('description', '')}",
    ]
    if item.get("brand"):
        lines.insert(1, f"- Brand: {item['brand']}")
    return "\n".join(lines)


def _describe_wardrobe_item(item: dict) -> str:
    """One wardrobe piece on one line, with its notes when it has any."""
    line = (
        f"- {item.get('name', '')} ({item.get('category', '')}; "
        f"{', '.join(item.get('colors') or [])}; "
        f"{', '.join(item.get('style_tags') or [])})"
    )
    if item.get("notes"):
        line += f" — {item['notes']}"
    return line


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "No outfit suggestion provided, so no fit card was created."

    title = new_item.get("title", "this piece")
    price = new_item.get("price")
    platform = new_item.get("platform", "")

    details = [
        f"- Item: {title}",
        f"- Price: ${price:.2f}" if isinstance(price, (int, float)) else "",
        f"- Platform: {platform}",
        f"- Condition: {new_item.get('condition', '')}",
        f"- Colors: {', '.join(new_item.get('colors') or [])}",
        f"- Style: {', '.join(new_item.get('style_tags') or [])}",
    ]
    if new_item.get("brand"):
        details.insert(1, f"- Brand: {new_item['brand']}")

    prompt = (
        "Write a caption for a social post about this thrift find.\n\n"
        + "\n".join(d for d in details if d)
        + f"\n\nHow it's being styled:\n{outfit.strip()}"
    )

    response = generate(prompt, system=_FIT_CARD_SYSTEM)

    if not response.strip():
        return f"New thrift find: {title} from {platform}. Styled and ready to wear."
    return response


_FIT_CARD_SYSTEM = (
    "You write captions people post about their thrift finds. Write two to "
    "four sentences in a casual first-person voice, like a real post, not a "
    "product description. Mention the item, its price, and the platform once "
    "each. Be specific about the vibe of the outfit. At most two hashtags. "
    "Return only the caption."
)
