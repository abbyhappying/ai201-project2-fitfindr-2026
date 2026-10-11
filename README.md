# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---



## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory


### `search_listings`

- **What it does:**Finds listings that match the description keywords, filters them by optional size and price ceiling, and returns them ranked by keyword overlap.
- **Inputs:**
description (str): keywords describing the item, e.g. "vintage graphic tee".

size (str | None): a size label, matched case-insensitively on whole tokens — "M" matches "S/M", but "S" does not match "US 9" and "L" does not match "XL". None skips size filtering.

max_price (float | None): price ceiling in US dollars, inclusive. None skips price filtering.
- **Returns:** up to 10 results (config.SEARCH_RESULT_LIMIT), best match first, as a list[dict], where each dict contains id, title, description, category, style_tags (list), size, condition, price (float), colors (list), brand (str or None), platform.
- **When it has nothing:**
Returns an empty list [] when nothing matches — it does not raise an exception.

### `suggest_outfit`

- **What it does:**
Asks the model for one or two outfits built around the new item. It uses the user's wardrobe pieces when they exist and general styling ideas when they don't.
- **Inputs:**
new_item (dict)  wardrobe (dict)
- **Returns:**
a non-empty str. With a populated wardrobe, it names specific pieces the user owns. With an empty one, it gives general ideas built on common basics and says so.
- **When it has nothing:**
When wardrobe["items"] is empty, suggest_outfit still calls the model, asking for general styling ideas built around the item using common basics. The returned text opens with a short sentence noting that the wardrobe is empty, then gives one or two general outfits. It never raises and never returns an empty string.

### `create_fit_card`

- **What it does:**
Writes a short social-post-style caption about the find, based on the outfit suggestion and the item.
- **Inputs:**
outfit (str): the output of suggest_outfit.
new_item (dict)
- **Returns:**
str, a fit card caption
- **When it has nothing:**
if outfit is empty or whitespace, it returns a descriptive message string ("No outfit suggestion provided, so no fit card was created.") without calling the model and without raising error.
---

## Planning Loop


**Branch rule:**
1. Call search_listings with the user's description, size, and price.
2. If the result is empty: set session["error"] to a message that names what was searched and which filters were applied, and add a hint such as "try a higher price or a different size". Then stop and return the session. Don't call either model tool.

3. Otherwise:
   - Store session["search_results"][0] in session["selected_item"].
   - Call suggest_outfit(session["selected_item"], session["wardrobe"]),
     reading the item back out of the session.
   - Store the result in session["outfit_suggestion"].

4. Call create_fit_card(session["outfit_suggestion"], session["selected_item"]),
   store the result in session["fit_card"].

5. Return the session.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:**
The query is parsed with regular expressions. A price ceiling is extracted from phrases like "under $30", "below 30", or "max $30". A size is extracted from phrases like "size M" or "in size XL". Whatever remains, with those phrases removed, becomes the description passed to search_listings. If no price or size phrase is found, those arguments are None.

**What moves through the session:**

1. query: the raw user text, kept for the record and for error messages.
2. parsed: extracted description, size, max_price: the parsed values, so you can see what the parser actually extracted. This is the first place to look when search results seem wrong.
3. search_results: the list returned by search_listings.
4. selected_item: search_results[0], the listing the rest of the run is built on.
5. wardrobe: the wardrobe passed in, so the record shows which one was used.
6. outfit_suggestion: the string from suggest_outfit.
7. fit_card: the string from create_fit_card.
8. error: empty unless the loop stopped early, in which case it holds the user-facing message.

---

## Sample Run



**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

```
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear**
Pair the baby tee with your **Baggy straight-leg jeans, dark wash** for a classic early 2000s proportion play—fitted on top and loose on the bottom. Layer the **Vintage black denim jacket** on top and finish with your **Chunky white sneakers** and **Black crossbody bag**.

**Outfit 2: Casual Contrast**
Tuck the tee into your **Wide-leg khaki trousers** to highlight the cropped fit and mix the pink and purple tones with earthy tan. Throw on the **Black cropped zip hoodie** open over it, and ground the look with your **Black combat boots**.

  Fit card: Just scored this dreamy butterfly baby tee on depop for only eighteen bucks and I am obsessed withthe pink and purple print. I'm leaning into total Y2K streetwear today by pairing the fitted crop with baggy dark-wash jeans and chunky white sneakers. It gives me major early 2000s mall-rat energy in the best way possible. #y2kstyle #depopfinds

0 model calls this session, 2 served from cache

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxyfit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition':'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

**Outfit 1: Casual Streetwear**
Pair the vintage Levi's 501s with the white ribbed tank top tucked in, layered under the black cropped zip hoodie. Finish with the chunky white sneakers and the black crossbody bag for an effortless, classic look that highlights the medium wash.

**Outfit 2: Cozy Grunge**
Wear the vintage Levi's 501s with the oversized grey crewneck sweatshirt draped loosely over top. Add the black combat boots and the brown leather belt to contrast the grey and blue tones with some rugged texture.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Scored these vintage Levi’s 501s on Depop for just $38 and they fit like an absolute dream. I’m styling them with crisp white sneakers for that effortlessly cool, casual streetwear vibe. So stoked on this wash! #VintageDenim #DepopFinds
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
  I gave the AI my `search_listings` Tool Inventory spec
  and asked it to implement the size filter.
- *What came back:*
   It wrote a plain substring test:
  `if size.lower() in listing["size"].lower()`.
- *What I changed:*
  That matches `"s"` inside `"us 9"` and `"l"` inside
  `"xl"` — the exact trap the docstring warns about, and it would have made
  Criterion 1 flaky. I replaced it with token-based matching: split both
  sizes into whole tokens (`_size_tokens`) and check that the wanted tokens
  are a subset of the listing's tokens. Now `"M"` matches `"S/M"` but not
  `"US 9"`.

**Moment 2**

- *What I asked for:*
 I asked the AI how `run_agent` should handle the case
  where `search_listings` returns nothing.
- *What came back:*
   It suggested returning `None` and letting the loop check
  `if not results`.
- *What I changed:*
  `None` and `[]` are both falsy, so the branch would still
  fire, but `None` breaks the spec — my Tool Inventory says "returns an empty list, not None". It also breaks any downstream `len(...)`. I kept `[]` and made the error message name the search and the filters: "No listings matched 'designer ballgown' with size XXS under $5. Try a higher price or a different size." That satisfies the Milestone 2 rule that "No results" is not an acceptable message.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.Full three-tool run returns a fit card  | 4 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |
| 2. Impossible query stops before the second tool | 5 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |
| 3. selected_item id == suggest_outfit input id | 5 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |
| 4. Fit card mentions title and price |  5 of 5 | FAIL |  FAIL|  FAIL|  FAIL|  FAIL| MISSED (0/5) |
| 5.  Empty wardrobe still completes|  5 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
Criterion 1：Full three-tool run returns a fit card
--From results/run_2026-10-10_2308_before.md, scenario happy path, produced by run_agent (agent.py) calling search_listings, suggest_outfit, and create_fit_card (tools.py):
--Output:
[5] create_fit_card
      in:  outfit=548 chars, new_item='Y2K Baby Tee — Butterfly Print'
      out: Just scored this butterfly print baby tee on depop for $18 and I am obsessed with the pastel colorway...
  try 1: completed — fit card 312 chars

```

```
Criterion 2：Impossible query stops before the second tool
--From results/run_2026-10-10_2308_before.md, scenario empty search, produced by the branch in run_agent (agent.py):
--Output:
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty, stopping before the model tools
  try 1: stopped early — No listings matched "designer ballgown" in size XXS under $5
```
```
Criterion 3：State consistency:selected_item id == suggest_outfit input id

From results/run_2026-10-10_2308_before.md, scenario state check, produced by trace.step() calls in run_agent (agent.py)
--Output:
[3] select_item
      in:  4 results
      out: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
      →    id=lst_004, best match first
[4] suggest_outfit
      in:  new_item='90s Track Jacket — Navy/White Stripe' (id=lst_004), wardrobe=10 items

```
```
Criterion 4：Fit card mentions title and price
--From results/run_2026-10-10_2308_before.md, scenario fit card (query: denim jacket under $50), try 1, produced by create_fit_card (tools.py).
--Output:
fit card  (example wardrobe)
  query: denim jacket under $50
[5] create_fit_card
      in:  outfit=546 chars, new_item='Denim Jacket — Light Wash, Cropped'
      out: Score this vintage Wrangler cropped denim jacket for just $42 on poshmark and honestly, I'm obsessed...
  try 1: completed — fit card 329 chars

```
```
Criterion 5：Empty wardrobe still completes
From results/run_2026-10-10_2308_before.md, scenario empty wardrobe, produced by suggest_outfit (tools.py) with an empty wardrob.
--Output:
[4] suggest_outfit
      in:  new_item='Platform Sneakers — White Chunky Sole' (id=lst_019), wardrobe=0 items
      out: Since I don't know what's in your closet yet, here are two easy ideas built around common basics!  **Outfit 1:...
  try 1: completed — fit card 266 chars
```
---

## Verdicts and Diagnoses



| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET (5/5) | All 5 tries of `vintage graphic tee under $30` show `stopped early: no` and a non-empty fit card in `results/run_2026-10-10_2308_before.md`. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET (5/5) | All 5 tries of `designer ballgown size XXS under $5` show `search_results: 0`, the `branch: empty` trace line, no `suggest_outfit` step, and an error naming the search, both filters, and what to change. |
| 3 | `selected_item` id == `suggest_outfit` input id | 5 of 5 | MET (5/5), but the check is weak | In all 5 tries the `select_item` line and the `suggest_outfit` line both show `id=lst_004`. But both lines print `session['selected_item']['id']`, so the trace compares the value to itself. It could not have failed (see diagnosis below). |
| 4 | Fit card mentions the item's title and price | 5 of 5 | **MISSED (0/5)** | I checked each card from the `fit card` scenario for the literal title `Denim Jacket — Light Wash, Cropped` and the price `$42`. The price appears 5/5; the title appears 0/5 (every card paraphrases it as "vintage Wrangler cropped denim jacket"). Both are required, so every try fails. |
| 5 | Empty wardrobe still completes | 5 of 5 | MET (5/5) | All 5 tries of `platform sneakers size US 8` with an empty wardrobe show `wardrobe=0 items`, an outfit that opens by saying the closet is empty, and a fit card. |

**Diagnoses**

**Criterion 4: the fit card misses the title (MISSED 0/5)**

- **Step:** `[5] create_fit_card`, the last step in `run_agent` (agent.py), which calls `create_fit_card` in tools.py.
- **Place:** the model's output.
- **Mechanism:** `create_fit_card` sends the model the exact title (`- Item: Denim Jacket — Light Wash, Cropped`) and price (`- Price: $42.00`). But `_FIT_CARD_SYSTEM` tells it to *"write… like a real post, not a product description"* and only to *"Mention the item"*. A listing title is product-description text, so following the first instruction means rewriting it. All 5 cards turn it into casual words ("vintage Wrangler cropped denim jacket"), pulling "Wrangler" from the description rather than the title. Nothing in the prompt says to use the item's name as written, so the model never does. The price survives only because "$42" already reads like something a person would post. The same prompt let 2 of 5 `happy path` cards write "eighteen bucks" instead of `$18`, so the price is exposed to the same pressure.

**Why it isn't the other three places:**

- **Not the session:** the right item reached the step. The trace shows `select_item … id=lst_007` and then `create_fit_card in: new_item='Denim Jacket — Light Wash, Cropped'` in all 5 tries.
- **Not the loop's branch:** there is no decision at this step. The run completed all 5 tries (`stopped early: no`) and the branch never fired.
- **Not the tool's code:** `create_fit_card` puts both the title and the price into the prompt, and the price in every card is correct (`$42`), which shows the item's data arrived. The tool also returned a non-empty card every time, so the empty-response fallback never ran.

**Fix this points to:** change the prompt in `_FIT_CARD_SYSTEM`, not the loop. Tell the model: *"Use the item's name exactly as given in the Item line, once"* and *"write the price in digits exactly as given, e.g. $42"*. Also pass the price as `${price:g}` (`$42`) instead of `$42.00`.

*Note on scoring:* "mentions the title" was loose enough that a paraphrase could be argued either way. I scored it as a literal match, because that's the only reading I can check the same way every time.

**Criterion 3: met, but the measurement can't fail (place: the session/trace).**
The `suggest_outfit` trace line in `run_agent` builds its `id=` from `session['selected_item']`, the same field the `select_item` line reads. So the trace proves the session field was set, not what `suggest_outfit` actually received. A bug that passed `results[1]` to the tool would still show matching ids. To make it real, the id has to be recorded inside `suggest_outfit` from its own `new_item` argument.

**A failure outside the run log: non-empty results that are the wrong item (place: the loop's branch + a tool's return shape).**
I fed probe queries through `parse_query` and `search_listings` with no model calls:

```
'vintage ballgown'        -> 10 results, top: Vintage Levi's 501 Jeans — Medium Wash
'platform sneakers size 8'-> size=None (description='platform sneakers size 8')
'leather boots size 7.5'  -> size=None, top: Platform Mary Janes — Black Patent (US 7)
'black dress size medium' -> size=None, top: Platform Mary Janes — Black Patent (US 7)
```

There are two mechanisms. (1) `search_listings` keeps any listing with `score > 0`, so one shared word ("vintage") is enough. It returns no information about which words matched. My branch only tests `if not results`, so a list with one weak match goes straight to `suggest_outfit`, and the agent styles jeans as a ballgown. (2) The `_SIZE` regex in `parse_query` only reads letter sizes, `W30 L30`, and `US 8`. A bare `size 8` or `size medium` isn't parsed: the size filter is silently dropped and "size 8" becomes search keywords. My Criterion 5 scenario uses `size US 8` precisely to get around this, which is why Criterion 5 didn't catch it.

**Pattern:** every problem above is the same mistake. The agent treats "something came back" as "the right thing came back". That covers the search returning a weak match, the parser returning `size=None`, the model returning a card that names *an* item, and the trace showing *an* id. None of these steps checks its output against what the user actually asked for.

**Failure modes, triggered and handled**

** Empty search **
```
python app.py ask 'designer ballgown size XXS under $5'

  No listings matched "designer ballgown" in size XXS under $5. Try: raise your price limit; try a different size or leave the size out; use fewer or broader words (e.g. 'tee' instead of 'designer graphic tee').

0 model calls this session
```
** Empty wardrobe **
```
python app.py ask 'vintage graphic tee under $30' --empty-wardrobe
(running with an empty wardrobe)

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Since your wardrobe is a blank slate, here are a couple of easy outfit ideas using closet basics.

**Outfit 1: Casual Y2K Streetwear**
Pair the baby tee with classic light-wash blue denim jeans and white canvas sneakers. The fitted crop top balances the relaxed denim, and white sneakers keep it fresh and effortless.

**Outfit 2: Sweet & Sporty**
Wear it tucked into a plain black tennis skirt with comfortable low-top sneakers and a simple canvas tote bag. The black skirt makes the pink and purple butterfly graphic pop while keeping the look cute and wearable.

  Fit card: Obsessed with this little pink and purple butterfly tee I just scored on Depop for only $18! I threw it on with a black tennis skirt and my favorite tote for the cutest sweet-and-sporty vibe. It’s seriously giving all the early 2000s nostalgia. #y2kstyle #depopfinds

2 model calls this session, 470 prompt + 195 output tokens
```
** Model unavailable **
```
python app.py ask 'platform sneakers size 8'

  Found a match (Platform Sneakers — White Chunky Sole), but the model couldn't be reached. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

1 model calls this session
```

## Loop Trace


**Happy path**

```
python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select_item
      in:  10 results
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    best match first
[4] suggest_outfit
      in:  new_item='Y2K Baby Tee — Butterfly Print', wardrobe=10 items
      out: **Outfit 1: Y2K Streetwear** Pair the baby tee with your **Baggy straight-leg jeans, dark wash** for a classic…
[5] create_fit_card
      in:  outfit=573 chars, new_item='Y2K Baby Tee — Butterfly Print'
      out: Just scored this dreamy butterfly baby tee on depop for only eighteen bucks and I am obsessed with the pink an…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear**
Pair the baby tee with your **Baggy straight-leg jeans, dark wash** for a classic early 2000s proportion play—fitted on top and loose on the bottom. Layer the **Vintage black denim jacket** on top and finish with your **Chunky white sneakers** and **Black crossbody bag**.

**Outfit 2: Casual Contrast**
Tuck the tee into your **Wide-leg khaki trousers** to highlight the cropped fit and mix the pink and purple tones with earthy tan. Throw on the **Black cropped zip hoodie** open over it, and ground the look with your **Black combat boots**.

  Fit card: Just scored this dreamy butterfly baby tee on depop for only eighteen bucks and I am obsessed with the pink and purple print. I'm leaning into total Y2K streetwear today by pairing the fitted crop with baggy dark-wash jeans and chunky white sneakers. It gives me major early 2000s mall-rat energy in the best way possible. #y2kstyle #depopfinds

0 model calls this session, 2 served from cache
```

**Empty search**

```
python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: description='designer ballgown', size='XXS', max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty, stopping before the model tools

  No listings matched "designer ballgown" in size XXS under $5. Try: raise your price limit; try a different size or leave the size out; use fewer or broader words (e.g. 'tee' instead of 'designer graphic tee').

0 model calls this session
```

**Size not parsed** (the bug from the diagnosis above: `size 8` is not read as a size, so the filter is dropped and the run continues)

```
python app.py ask 'platform sneakers size 8' --trace
[1] parse_query
      in:  platform sneakers size 8
      out: description='platform sneakers size 8', size=None, max_price=None
[2] search_listings (via MCP)
      in:  description='platform sneakers size 8', size=None, max_price=None
      out: 5 items: Platform Sneakers — White Chunky Sole, Platform Mary Janes — Black Patent, Low-Top Canvas Sneakers — Off-White … +2 more
[3] select_item
      in:  5 results
      out: Platform Sneakers — White Chunky Sole ($48.0, poshmark)
      →    best match first
[4] suggest_outfit
      in:  new_item='Platform Sneakers — White Chunky Sole', wardrobe=10 items
      out: **Outfit 1: Y2K Streetwear** Pair the platform sneakers with your **Baggy straight-leg jeans, dark wash** and …
[5] create_fit_card
      in:  outfit=535 chars, new_item='Platform Sneakers — White Chunky Sole'
      out: Obsessed with these chunky white platform sneakers I just scored on Poshmark for $48. They totally make the ba…

  Found:    Platform Sneakers — White Chunky Sole — $48.0 on poshmark

  Outfit:   **Outfit 1: Y2K Streetwear**
Pair the platform sneakers with your **Baggy straight-leg jeans, dark wash** and the **Black cropped zip hoodie**. The chunky Velcro shoes match the 2000s streetwear vibe of the low-hip jeans and the cropped fit of the hoodie.

**Outfit 2: Casual Minimal**
Style the sneakers with your **Wide-leg khaki trousers** and the **White ribbed tank top**, layered under the **Vintage black denim jacket**. The crisp white shoes tie into the tank top, while the platform adds a cool edge to the tailored trousers.

  Fit card: Obsessed with these chunky white platform sneakers I just scored on Poshmark for $48. They totally make the baggy jeans and cropped hoodie look for that ultimate 2000s streetwear vibe. Can't wait to style them with wide-leg trousers next! #thriftfinds #y2kstyle

2 model calls this session, 676 prompt + 192 output tokens
```

**On the MCP move:**
```
I wrapped search_listings in mcp_server.py with @mcp.tool(), registered it with the same name and typed inputs as my Tool Inventory. In run_agent() I replaced search_listings(description, size, max_price) with call_tool("search_listings", {...}). The call shape changed but the return value did not — still a list[dict] with the same fields. python mcp_client.py confirmed the tool was listed. One full query ran end to end with no difference in output.

Nothing behaved differently after the move: in both eval runs (before and after, 25 tries each), every try's trace shows `search_listings (via MCP)`, every matching query selected the same top item (lst_002, lst_004, lst_007, lst_019), and the empty-search branch still stopped before suggest_outfit 5 of 5 times, so the list[dict] coming back over MCP was handled exactly like the direct call's.
```



---

## The Improvement


**What I changed:**
I rewrote one prompt, _FIT_CARD_SYSTEM in tools.py, which is the system prompt for create_fit_card. I removed "not a product description" and the loose "Mention the item, its price…". In their place are two explicit rules: use the item's name exactly as written on the Item line, word for word, and write the price exactly as written on the Price line, in digits with the $ sign.

**Which failure it was meant to fix:**
Criterion 4, "Fit card mentions the item's title and price," was MISSED at 0/5 in the before run. The price appeared every time, but every card paraphrased the title (Denim Jacket — Light Wash, Cropped became "vintage Wrangler cropped denim jacket"). My diagnosis was that the old prompt told the model to write "not a product description" and never asked it to keep the title, so rewriting the title was the model following its instructions. The same prompt also let 2 of 5 happy-path cards write "eighteen bucks" instead of $18, so the price was at risk for the same reason.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.Full three-tool run returns a fit card  | 4 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |
| 2. Impossible query stops before the second tool | 5 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |
| 3. selected_item id == suggest_outfit input id | 5 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |
| 4. Fit card mentions title and price |  5 of 5 | PASS |  FAIL|  PASS|  FAIL|  PASS| MISSED (3/5) |
| 5.  Empty wardrobe still completes|  5 of 5 | PASS |  PASS|  PASS|  PASS|  PASS| MET (5/5) |

**Real output**, pasted as text, naming the file and function that produced it:

```
Criterion 4：Fit card mentions title and price — PASS
--From results/run_2026-10-11_0803_after.md, scenario fit card (query: denim jacket under $50), try 1, produced by create_fit_card (tools.py).
--Output:
[5] create_fit_card
      in:  outfit=494 chars, new_item='Denim Jacket — Light Wash, Cropped'
      out: I am obsessed with this vintage Denim Jacket — Light Wash, Cropped I just scored on poshmark! For $42.00, it's…
Fit card:
I am obsessed with this vintage Denim Jacket — Light Wash, Cropped I just scored on poshmark! For $42.00, it's the ultimate piece for nailing that effortless double denim streetwear vibe with chunky kicks. #ThriftFind #Streetwear
```

```
Criterion 4：Fit card mentions title and price — FAIL
--From results/run_2026-10-11_0803_after.md, scenario fit card (query: denim jacket under $50), try 2, produced by create_fit_card (tools.py).
--Output:
Fit card:
Just scored this Wrangler on poshmark for only $42.00 and I am so obsessed with how it looks layered with baggy dark denim and chunky sneakers. It gives off the ultimate effortless streetwear energy. #thrifffind #streetwear
```

No MCP move in this change. This is a prompt-only change to _FIT_CARD_SYSTEM in tools.py.

**Did it help, and how do I know:**

The prompt rewrite helped but didn't meet the target: criterion 4 went from 0/5 to 3/5 because the model now copies the exact title most of the time, but in 2 of 5 tries it still used the brand "Wrangler" from the outfit text instead, so a prompt alone can't guarantee 5/5 without a check in code.



---

## What's Still Broken


**Criterion 4: Fit card mentions the item's title and price (still MISSED, 3/5)**

The prompt rewrite moved it from 0/5 to 3/5. The price now appears 5/5, but the title is still dropped in 2 of 5 tries. Both failures replace it with the brand: "this Wrangler" (try 2) and "this Wrangler jacket" (try 4). The brand comes from the outfit text that `create_fit_card` receives: `suggest_outfit` calls the item "your Wrangler jacket" every time, so the model sees two names for it and sometimes picks the casual one. The temperature is 0.9, and the prompt still asks for a casual voice that conflicts with a product-style title. That means a prompt alone raises the rate but can't guarantee it.

**What I'd do next:** check the output in code instead of relying on the prompt. After `generate()` returns, `create_fit_card` would check that the card contains the exact title (after normalizing case, dashes, and whitespace) and the price. If either is missing, it retries once with a hint naming what was left out. If the retry also fails, it appends `(title, $price on platform)` to the card so it never returns without them. That turns 5/5 from "likely" into something the code enforces. I'd also format the price as `$42` instead of `$42.00` so the prompt and the check use the same string.

**Why I stopped here:** the unit asks for one change, measured properly. The prompt rewrite was that change, and it went straight at the cause I diagnosed. Adding the check in the same run would have mixed two fixes, and I couldn't have said which one moved the number. The 3/5 shows how far the prompt alone gets, and the two failures point to the next fix.

## How I Used AI
**Moment 1**

What I asked for: I asked AI to review the _FIT_CARD_SYSTEM prompt in tools.py for create_fit_card and tighten the wording so the model stops paraphrasing item names and prices.

What came back: It suggested removing "not a product description" and the vague "Mention the item, its price…" line, and replacing them with two explicit rules: copy the item name word for word from the Item line, and copy the price in digits with the $ sign exactly as written on the Price line. It also flagged that the loose phrasing was probably why the model kept softening/rephrasing values.

What I changed: I rewrote _FIT_CARD_SYSTEM with those two rules in place of the old lines. This was a prompt-only change — no MCP move.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
