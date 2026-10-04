"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    # 1. Start a session.
    session = new_session(query, wardrobe)

    # 2. Count each step and check the stop condition before running it.
    count = 0

    # 3. Parse the query.
    count += 1
    trace.check_iterations(count)
    description, size, max_price = parse_query(query)
    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # 4. Search.
    count += 1
    trace.check_iterations(count)
    results = search_listings(description, size, max_price)
    session["search_results"] = results

    # THE BRANCH: nothing came back, so stop before either model tool runs.
    if not results:
        session["error"] = _no_results_message(description, size, max_price)
        return session

    # 5. Choose an item. Search returns best match first.
    session["selected_item"] = results[0]

    # print("BEFORE suggest_outfit, selected_item id:",
    #   session["selected_item"]["id"])

    # 6. Suggest an outfit.
    count += 1
    trace.check_iterations(count)
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )
    # print(session["search_results"][0]["id"])

    # 7. Write the fit card.
    count += 1
    trace.check_iterations(count)
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )

    # 8. Return the session.
    return session


# ── query parsing ─────────────────────────────────────────────────────────────

# "under $30", "below 30", "max $30", "less than $30", "up to $30"
_PRICE_BEFORE = re.compile(
    r"\b(?:under|below|max|less than|up to)\s*\$?\s*(\d+(?:\.\d+)?)", re.I
)
# "$30 or less", "$30 max"
_PRICE_AFTER = re.compile(r"\$\s*(\d+(?:\.\d+)?)\s*(?:or less|max)\b", re.I)

# "size M", "in size XL", "size S/M", "size US 8.5", "size W30 L30"
_SIZE = re.compile(
    r"\b(?:in\s+)?size\s+"
    r"(US\s*\d+(?:\.\d+)?|W\d+(?:\s*L\d+)?|[A-Za-z]{1,3}(?:/[A-Za-z]{1,3})?)\b",
    re.I,
)


def parse_query(query: str) -> tuple[str, str | None, float | None]:
    """
    Pull a price ceiling and a size out of the query with regex. Whatever is
    left, with those phrases removed, is the description.

    Returns (description, size, max_price). size and max_price are None when
    the query doesn't mention them.
    """
    text = query or ""

    max_price = None
    match = _PRICE_BEFORE.search(text) or _PRICE_AFTER.search(text)
    if match:
        max_price = float(match.group(1))
        text = text.replace(match.group(0), " ")

    size = None
    match = _SIZE.search(text)
    if match:
        size = match.group(1)
        text = text.replace(match.group(0), " ")

    description = re.sub(r"[,\s]+", " ", text).strip(" ,.")
    return description, size, max_price


def _no_results_message(
    description: str, size: str | None, max_price: float | None
) -> str:
    """Say what was searched, which filters were on, and what to change."""
    message = f'No listings matched "{description}"'
    if size:
        message += f" in size {size}"
    if max_price is not None:
        message += f" under ${max_price:g}"

    hints = []
    if max_price is not None:
        hints.append("raise your price limit")
    if size:
        hints.append("try a different size or leave the size out")
    hints.append("use fewer or broader words (e.g. 'tee' instead of 'designer graphic tee')")
    return f"{message}. Try: {'; '.join(hints)}."


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
