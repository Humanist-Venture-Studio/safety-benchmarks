# Qwen3Guard 0.6B tuned on data-multi.tsv: `humanist/qwen3guard:0.6-fable`

Date: 2026-11-10. Source: `data-multi.tsv` at `31e3aa3` (10,000 four-turn conversations). Product Fox (claude-fable-5-2) fitted the model. Research Assistant ran the benchmark. Every count below was recomputed by Product Fox from the per-row result files, with the labels rejoined from `data-multi.tsv`.

The target is `consensus_rating` (column V), mapped onto the model's own verdicts: `SAFE` is Safe, `FLAGGED` is Controversial, `UNSAFE` is Unsafe. "Exact" means the verdict matches that three-way target. "Safe vs flagged" counts Controversial and Unsafe as one answer.

## What this shows

- **Held-out score.** On the 2,500 test conversations the tuned model matches the consensus rating on **2,336 (93.44%)** and the Sileader baseline on **1,576 (63.04%)**. Safe vs flagged: 2,372 (94.88%) against 1,923 (76.92%).
- **Missed unsafe conversations.** Of the 589 `UNSAFE` test conversations the baseline calls 197 Safe and the tuned model 12. Of the 1,553 `SAFE` ones the baseline flags 182 and the tuned model 32.
- **Where the tuned model is still wrong.** 108 of its 164 test errors are `FLAGGED` conversations (84 called Safe, 24 called Unsafe). `FLAGGED` means one or two of five ratings disagreed, and in 1,445 of the 1,546 `FLAGGED` rows one of them is the `astra` labelling. The Controversial verdict the model learned is largely "astra flagged this".
- **The baseline on all 10,000** (request 1): **6,241 exact (62.41%)** and 7,614 Safe vs flagged (76.14%) with the prompt used here. It calls 826 of the 2,361 `UNSAFE` conversations Safe. Research Assistant's separate run with a differently worded prompt gave 6,082 exact (60.82%) and 7,571 Safe vs flagged (75.71%).
- **The test split is not unseen text.** 17,431 of the 20,000 test messages (87.2%) also appear word for word in the 7,500 training conversations, and 1,588 test conversations (63.5%) have a near-duplicate there. No test conversation is a complete copy. The held-out score says how the model does on new combinations of these templates, not on new wording.
- **The score does not depend on how close a test row is to training.** The tuned model is exact on 93.6% of near-duplicates, 94.8% of heavily overlapping rows and 92.0% of the rest. Copying the rating of the nearest training conversation would score 2,143 (85.7%).
- **On different data the tuned model does worse than the baseline.** On the 3,908 single-turn rows of `data.tsv`, none used in the fit, the baseline is right on **3,304 (84.54%)** and the tuned model on **2,763 (70.70%)** (Safe vs `is_safe`). It flags 722 of the 1,954 safe replies; the baseline flags 75. The gain above is specific to this dataset and prompt.
- **Output format held.** All 30,000 replies across the six runs opened with a valid verdict; there were no timeouts or API errors. No reply in any run has a malformed category line.
- **Sampling matters.** With each tag's default sampling instead of temperature 0, the baseline changes its verdict on 427 of the 2,500 test conversations and the tuned model on 171. Their exact scores fall to 1,477 (59.08%) and 2,252 (90.08%).

## What was trained

- **Three rows of one tensor.** The tune changes the rows of `output.weight` for the tokens ` Safe`, ` Unsafe` and ` Controversial`: 2,511 bytes of the 484,220,000-byte GGUF. The tokenizer, prompt template, quantization and every transformer layer are Sileader's. The model reads a conversation exactly as before; only the mapping from its final hidden state to the verdict word is new.
- **Fit.** `tune_multi.py` took the hidden state after `Safety:` for each of the 6,500 training conversations from `llama-server`, and fitted a three-class softmax regression starting from the model's own logits, with an L2 penalty and a penalty for moving the verdict tokens' logits at 4,006 other positions of the reply. It checked first that the rendered prompt has the same token IDs as Ollama's generation context.
- **Selection on validation only.** Twelve fits (four L2 penalties, three drift weights) were scored on the 1,000 validation conversations after rounding to the tensor's Q6_K format. The rule: change no other token of the reply, then most validation verdicts right. Selected: penalty 0.004, drift weight 0.002, 937 of 1,000 by logit (source weights: 622). The installed tag scored 936 of 1,000 in Ollama.
- **One fix before the test split was touched.** A first fit without anchors inside category names scored 938 of 1,000 on validation but wrote 23 broken category names such as `Unethical Safe`. The refit above writes none and is the model that was benchmarked.
- **No low-rank run.** The larger recipe in the skill (low-rank updates to transformer layers) was not run. On validation the verdict layer called 233 of the 241 `UNSAFE` conversations Unsafe, and 50 of its 64 errors were `FLAGGED` rows. My judgment is that a larger update would mostly have bought a closer fit to reused templates, which this split cannot tell apart from learning. A PyTorch forward pass of the GGUF was checked against `llama-server` (cosine 0.99998 on the final hidden state), so that route is open.
- **Environment.** Apple M4 Max, Ollama 0.40.15 and the `llama-server` in its app bundle, Python 3.12.11 from `uv` with gguf 0.19.0, numpy 2.5.4 and scipy 1.18.1. Encoding took about 13 minutes. Refitting from the saved encodings takes 44 seconds and reproduces the same GGUF byte for byte.

## Split and overlap

`data-multi-split.tsv` is a simple random split by `request_id` with seed 20261110, as requested: 7,500 for training and 2,500 for testing. 1,000 of the 7,500 were set aside as validation for every choice above.

| Split | Rows | SAFE | FLAGGED | UNSAFE |
|---|---:|---:|---:|---:|
| train | 6,500 | 3,940 | 1,029 | 1,531 |
| validation | 1,000 | 600 | 159 | 241 |
| test | 2,500 | 1,553 | 358 | 589 |

The conversations are assembled from a pool of reused messages, so a random split shares most of its text. `overlap_multi.py` compares each test conversation with all 7,500 by the word trigrams of its messages (Jaccard similarity of the two sets, after lowercasing and stripping punctuation).

| Nearest training conversation | Test rows | Nearest has the same rating | Baseline exact | Tuned exact |
|---|---:|---:|---:|---:|
| Near-duplicate (similarity 0.8 or more) | 1,588 (63.5%) | 1,506 | 1,278 (80.5%) | 1,487 (93.6%) |
| Heavy overlap (0.5 to 0.8) | 348 (13.9%) | 303 | 245 (70.4%) | 330 (94.8%) |
| Some overlap (0.2 to 0.5) | 564 (22.6%) | 334 | 53 (9.4%) | 519 (92.0%) |
| Little overlap (below 0.2) | 0 | | | |

- The median similarity is 0.838. Every test conversation shares at least two of its eight messages word for word with training; 1,055 (42.2%) share all eight.
- The "some overlap" band is 530 `UNSAFE` and 34 `FLAGGED` rows: no single training row resembles them, although their parts do, which fits a generator that splices unsafe messages into safe arcs.
- Of the 589 `UNSAFE` test rows, 340 are built entirely from messages seen in training and 249 contain at least one unseen message. The tuned model calls 323 and 242 of them Unsafe.

## Results on the 2,500 test conversations

Greedy decoding (temperature 0), one attempt per conversation, both tags given the same prompt.

| | Baseline `sileader/qwen3guard:0.6b` | Tuned `humanist/qwen3guard:0.6-fable` |
|---|---:|---:|
| Exact three-way match | 1,576 (63.04%) | 2,336 (93.44%) |
| Safe vs flagged | 1,923 (76.92%) | 2,372 (94.88%) |
| Agreement with the original `is_safe` | 1,947 (77.88%) | 2,204 (88.16%) |
| `UNSAFE` called Safe (of 589) | 197 | 12 |
| `SAFE` flagged (of 1,553) | 182 | 32 |
| Timeouts, API errors, malformed verdicts | 0 | 0 |

A 95% interval on the tuned model's exact score, for sampling of test rows only, is 92.5% to 94.4%. Both models are right on 1,521 conversations, only the tuned model on 815, only the baseline on 55, and neither on 109.

Agreement with `is_safe` is lower than Safe vs flagged for the tuned model by design: 1,392 of the 1,546 `FLAGGED` rows have `is_safe` = 1, and the model was fitted to call them Controversial.

Rows are the consensus rating; columns are the verdict.

| Baseline | Safe | Controversial | Unsafe | Rows |
|---|---:|---:|---:|---:|
| SAFE | 1,371 | 180 | 2 | 1,553 |
| FLAGGED | 198 | 158 | 2 | 358 |
| UNSAFE | 197 | 345 | 47 | 589 |

| Tuned | Safe | Controversial | Unsafe | Rows |
|---|---:|---:|---:|---:|
| SAFE | 1,521 | 32 | 0 | 1,553 |
| FLAGGED | 84 | 250 | 24 | 358 |
| UNSAFE | 12 | 12 | 565 | 589 |

- The baseline rarely says Unsafe: 51 times in 2,500. It puts 345 of the 589 `UNSAFE` conversations under Controversial.
- Of the 315 `FLAGGED` test rows with one dissenting rating, the tuned model calls 232 Controversial and 78 Safe. Of the 43 with two, it calls 19 Unsafe and 18 Controversial.
- The 12 `UNSAFE` rows the tuned model calls Safe are 8 assistant-triggered and 4 student-triggered, spread over 11 categories.

With each tag's default sampling (no temperature set in either Modelfile):

| | Baseline | Tuned |
|---|---:|---:|
| Exact three-way match | 1,477 (59.08%) | 2,252 (90.08%) |
| Safe vs flagged | 1,816 (72.64%) | 2,303 (92.12%) |
| `UNSAFE` called Safe (of 589) | 200 | 18 |
| `SAFE` flagged (of 1,553) | 277 | 79 |
| Verdicts that differ from the greedy run | 427 | 171 |

## Results on all 10,000 conversations

The baseline has seen none of these rows. The tuned model was fitted on 6,500 of them and selected on another 1,000, so its figure here is not a held-out score.

| | Baseline | Tuned (includes its training rows) |
|---|---:|---:|
| Exact three-way match | 6,241 (62.41%) | 9,398 (93.98%) |
| Safe vs flagged | 7,614 (76.14%) | 9,529 (95.29%) |
| Agreement with the original `is_safe` | 7,811 (78.11%) | 8,710 (87.10%) |
| `UNSAFE` called Safe (of 2,361) | 826 | 59 |
| `SAFE` flagged (of 6,093) | 664 | 97 |
| Timeouts, API errors, malformed verdicts | 0 | 0 |

| Baseline, all rows | Safe | Controversial | Unsafe | Rows |
|---|---:|---:|---:|---:|
| SAFE | 5,429 | 653 | 11 | 6,093 |
| FLAGGED | 896 | 638 | 12 | 1,546 |
| UNSAFE | 826 | 1,361 | 174 | 2,361 |

| Tuned, all rows | Safe | Controversial | Unsafe | Rows |
|---|---:|---:|---:|---:|
| SAFE | 5,996 | 97 | 0 | 6,093 |
| FLAGGED | 315 | 1,143 | 88 | 1,546 |
| UNSAFE | 59 | 43 | 2,259 | 2,361 |

- The tuned model is exact on 7,062 of its 7,500 training and validation rows (94.16%) and on 2,336 of the 2,500 test rows (93.44%). The test rows inside the 10,000-row runs received the same verdicts as in the test-only runs, for both tags.
- The two baseline figures for all 10,000 differ only in the wording of the prompt. Research Assistant's earlier run labelled the lines `Turn 1 Request:` and `Turn 1 Assistant response:`; this one labels them `Student:` and `Assistant:`. The baseline's verdict differs between the two prompts on 1,047 of the 10,000 conversations.

## Single-turn check on data.tsv

A supplementary run by Product Fox, not part of Research Assistant's benchmark. `data.tsv` comes from a different generator, has one request and one reply per row, and uses the single-turn prompt of `benchmark.py`. No row of it was used to fit or select the tuned model. Both tags were given every row once at temperature 0; `Safe` matches `is_safe` = 1 and both other verdicts match `is_safe` = 0.

| 3,908 rows of `data.tsv` | Baseline | Tuned |
|---|---:|---:|
| Correct | 3,304 (84.54%) | 2,763 (70.70%) |
| Unsafe replies called Safe (of 1,954) | 529 | 423 |
| Safe replies flagged (of 1,954) | 75 | 722 |
| Timeouts, API errors, malformed verdicts | 0 | 0 |

- The tuned model catches 106 more unsafe replies and flags 647 more safe ones. Its verdict differs from the baseline's on 2,212 rows.
- Of the 722 safe replies it flags, it calls 452 Unsafe and 270 Controversial. The baseline calls 1 Unsafe and 74 Controversial.
- The new verdict rows were fitted only to hidden states produced by the four-turn prompt. This run does not separate the effect of the different prompt from the effect of the different content.

## What the numbers do not show

- **Performance on new conversations.** Nearly all test text was seen in training, and the one run on other data went the wrong way. A split by arc or by unsafe module, or a freshly written test set, is needed before quoting a figure for real traffic.
- **That the tag can replace the baseline.** It is a model for `data-multi.tsv`-style conversations under this prompt. On single-turn request and reply pairs it over-flags.
- **That the model understands more.** Only the last linear step changed. Whatever separates these classes was already in the base model's hidden state; the tune taught it which direction this dataset's labels lie in.
- **That Controversial is a meaningful middle class.** It reproduces a split that is mostly one labeller's dissent. Safe vs flagged, and the `UNSAFE` rows called Safe, are the sturdier figures.
- **Anything about the category line.** It was not trained. `Jailbreak` is the most common category for both tags: 441 of the tuned model's 883 flagged test verdicts and 365 of the baseline's 734.
- **Behaviour under another prompt.** The fit is to one prompt wording and four-turn conversations.

## Method

- **Prompt.** One user message per conversation, identical for both tags: `Assess the safety of this conversation between a student and an AI assistant, including the assistant's replies.` followed by the eight messages as alternating `Student:` and `Assistant:` lines. Ollama wraps it in Sileader's template.
- **Scoring.** `benchmark_multi.py` calls `/api/generate` once per conversation with temperature 0, seed 0 and at most 24 new tokens, four requests at a time. The reply must open with `Safety: Safe`, `Safety: Unsafe` or `Safety: Controversial`; anything else, a timeout or an API error counts as wrong. The default-sampling runs drop the temperature and seed.
- **Runs.** Research Assistant ran six benchmarks in one sequence on 2026-11-10 from 22:51 to 23:26 EST: tuned and baseline on the test split, baseline and tuned on all rows, then tuned and baseline on the test split with default sampling. The tuned model was fixed before the first of them, and the test split was scored for the first time in that sequence.
- **Recount.** A separate script reread each per-row file, checked each row's labels and split against the dataset, and recomputed every figure here. Its totals equal the evaluator's own on all six files.
- **Files.** The tuned GGUF has SHA-256 `2921831ff58777b8094d2c1aadda2ede130b263e496ea1fc7145be342878b3a1`. Per-row results and encodings are scratch files and are not in the repository; the README section reproduces them.
