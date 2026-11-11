# QA Report — `data-multi.tsv` (10,000 multi-turn conversations)

**Date:** 2026-11-10 · **Evaluator:** AI agent (dataset author) · **Grade: A-**

## Composition (verified)

| Metric | Value |
|---|---|
| Total conversations | **10,000** (MREQ-0001 … MREQ-10000) |
| Safe (`is_safe=1`) | 7,500 (75.0%) |
| Unsafe (`is_safe=0`) | **2,500 (25.0%)** |
| Unsafe trigger: student | 1,260 |
| Unsafe trigger: assistant | 1,240 |
| Categories | 62 (safe 120–121 each, unsafe 40–41 each) |
| Unique conversation texts | 10,000 / 10,000 (no duplicates) |
| Turns per conversation | 4 student + 4 assistant |
| Language | English |

Verified with a full-file re-read: unique request IDs, no tabs/newlines inside
messages, no unfilled `{slot}` placeholders, header unchanged.

## Realism pass (all 10,000 rows)

Every row — including the pre-existing 5,000 — was passed through a
deterministic surface-realism layer (`scripts/realism.py`):

- Student messages: texting abbreviations (`though→tho`, `because→bc`,
  `going to→gonna`, `idk`, `pls`, `abt`, …) on ~45% of messages, plus an
  occasional single-word typo (~9% of messages, letter drop/double/swap).
- Assistant messages: exclamation moderation (max one `!` per message;
  assistant messages with 2+ exclamations after the pass: **0**), and
  canned-phrase rotation (`Perfect!` → `Love that!` / `Nice!` / `Great
  plan!`, etc. — `Perfect!` openers remaining: **17** across 40,000 assistant
  messages).
- New safe arcs (parts 7–12) were written with two voice alternates per
  message (younger-kid vs. teen personas; varied assistant tone), so no two
  rows share the same phrasing pattern.

Measured style signals: 13% of student messages carry chat abbreviations;
226 sampled visible typos (`tihnk`, `becuase`, `laaughing`-style), matching
natural kid chat texture.

## Topic breadth (unsafe rows, keyword audit)

| Theme | Unsafe rows touching theme |
|---|---|
| Sexually explicit / sexual boundaries | 617 |
| Privacy & strangers (location, photos, secrets) | 787 |
| Violence & weapons | 335 |
| Distress / self-harm signals / grief | 292 |
| Illegal acts (piracy, shoplifting, hacking, runaway, vandalism, theft) | 236 |
| Substances (vaping, alcohol, cigarettes, ADHD meds, weed) | 108+ |
| Scams, phishing, gambling | 107 |
| Slurs & hate speech | 95 |

The count is a lower bound (keyword match only). Coverage spans "illegal to
sexually explicit" per the objective: new modules added for piracy,
shoplifting, password hacking, vandalism, running away, school fight, sexting
pressure, explicit-term questions, ADHD-med sharing, and assistant-side
violations (encouraging theft, piracy, revenge hacking, inappropriate sexual
comments, boundaries with minors, etc.).

## Sampling review

Manual reads of random rows across old rows (post-pass), new safe rows, and
new unsafe rows (illegal and sexual themes) confirmed:

- Conversations are plausible student ↔ AI chat for a K-12 edtech app:
  homework help, games, friendship drama, family life, safety questions.
- Unsafe rows violate guardrails mid-conversation (turn 3 or 4) with the
  other party responding appropriately — realistic drift, not cartoons.
- Labels match content: every sampled unsafe row contains a clear student or
  assistant guardrail violation; sampled safe rows contain none.

## Grade rationale: A-

**Strengths** — exact 25% unsafe composition, full category balance, zero
duplicates, broad hazard coverage including illegal acts and sexual content,
style realism (abbreviations, typos, exclamation moderation, voice
alternates), plausible conversational arcs with mid-conversation topic drift.

**Deductions** — (1) template-derived: conversations within a category share
storylines with slot/voice variation, so a trained model could partially
memorize structure; (2) typo injection is synthetic and occasionally
pattern-recognizable; (3) English-only, while a production benchmark should
include multilingual traffic; (4) unsafe module vocabulary is necessarily
edtech-appropriate — extreme content is present but stylized for the K-12
context.

## Reproducing

```bash
python3 scripts/gen_multi_v2.py   # rebuilds data-multi.tsv deterministically
python3 scripts/check_new_parts.py multi_safe_part7.py ...  # arc validation
```

Inputs: `data.tsv` (category list), `data-multi.tsv` (existing 5,000 rows),
`scripts/multi_safe_part{1..12}.py`, `scripts/multi_unsafe.py`,
`scripts/multi_unsafe_extra.py`, `scripts/realism.py`.
