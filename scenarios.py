"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    # Criterion 1: happy path
    {
        "name": "happy path",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    # Criterion 2: empty search
    {
        "name": "empty search",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    # Criterion 3: state consistency — compare the select_item and
    # suggest_outfit ids in the trace.
    {
        "name": "state check",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    # Criterion 4: fit card invariants
    {
        "name": "fit card",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 4,
    },
    # Criterion 5: empty wardrobe. "size US 8", not "size 8" — parse_query
    # only reads shoe sizes with the US prefix.
    {
        "name": "empty wardrobe",
        "query": "platform sneakers size US 8",
        "wardrobe": "empty",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
