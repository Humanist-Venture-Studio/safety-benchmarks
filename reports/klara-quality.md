# Klara dataset: composition and quality checks

`data/data-klara.tsv` holds 10,000 synthetic conversations between a K-12 student and an AI tutor, written one at a time by a language-model bot (Research Assistant) from scenario seeds, to train and test detectors of conversations in which a legally compliant tutor product would have to act. Every number here was recounted by the coordinating bot (Product Fox) from per-row files.

## Composition

Computed from `data/data-klara.tsv` (sha256 `0ff32b946a2e83760e90ce0974c73cedff23a6b8cbd9bd766cef155744caf294`), 18 November 2026.

- Rows: 10000. Columns: 25. Language: English. One conversation per row; a turn is one student message plus one tutor reply.
- Split: {'train': 8000, 'test': 1000, 'validation': 1000}. Scenarios: 1250 (8 rows each); scenarios appearing in more than one split: 0.
- Scenario kinds: {'risk': 4000, 'ordinary': 6000} rows (500 risk scenarios x 8 rows, 750 ordinary scenarios x 8 rows).
- Label: 1000 unsafe, 9000 safe. In every turn bucket (1 to 5 turns): 1,800 safe and 200 unsafe. In every split x turn bucket the unsafe share is exactly 10%.
- Trigger of unsafe rows: {'assistant': 500, 'student': 500}. Clarity of unsafe rows: {'clear': 900, 'borderline': 100}.
- Safe rows: 1000 look-alikes (each linked to an unsafe row of the same scenario) and 8000 ordinary.
- Grade bands: {'elementary_3_5': 2728, 'middle_6_8': 3696, 'high_9_12': 3576}. Subjects: {'ELA': 2296, 'Math': 2248, 'Science': 1496, 'History': 1448, 'World Languages': 616, 'Computer Science': 584, 'Study Skills': 512, 'Health': 456, 'Arts': 344}.
- Topic categories: 31. Unsafe share by category ranges from 0.0% to 25.0%; the 10% share is exact per turn bucket and per split, not per category (the plan aimed for roughly 10% in every category; that is not met).

| category | rows | unsafe | share |
|---|---:|---:|---:|
| homework_help | 1288 | 102 | 7.9% |
| test_prep | 1160 | 150 | 12.9% |
| essay_feedback | 1096 | 134 | 12.2% |
| concept_explanation | 800 | 0 | 0.0% |
| reading_analysis | 448 | 112 | 25.0% |
| sensitive_academic_topic | 400 | 0 | 0.0% |
| reading_comprehension | 400 | 0 | 0.0% |
| math_word_problems | 400 | 0 | 0.0% |
| research_project | 320 | 0 | 0.0% |
| study_skills | 320 | 0 | 0.0% |
| makeup_packet | 296 | 74 | 25.0% |
| coding_help | 240 | 0 | 0.0% |
| creative_writing | 240 | 0 | 0.0% |
| language_practice | 240 | 0 | 0.0% |
| study_planning | 240 | 60 | 25.0% |
| school_feelings_benign | 240 | 0 | 0.0% |
| oral_presentation | 208 | 52 | 25.0% |
| college_and_career | 200 | 0 | 0.0% |
| code_debugging | 200 | 50 | 25.0% |
| off_topic_chat | 200 | 0 | 0.0% |
| word_problems | 200 | 50 | 25.0% |
| data_project | 160 | 40 | 25.0% |
| group_project | 144 | 36 | 25.0% |
| lab_report | 112 | 28 | 25.0% |
| art_critique | 112 | 28 | 25.0% |
| source_analysis | 104 | 26 | 25.0% |
| college_essay | 72 | 18 | 25.0% |
| vocab_practice | 64 | 16 | 25.0% |
| health_unit | 56 | 14 | 25.0% |
| grammar_drill | 32 | 8 | 25.0% |
| lab_safety | 8 | 2 | 25.0% |
- Words per message, safe rows: mean 15.1, median 13.0.
- Words per message, unsafe rows: mean 16.4, median 15.0.
- Student messages under 12 words: 55.3% of 30000. Total words in the dataset: 912,073.

## Unsafe rows by rule family (all splits / train / validation / test)

| rule_id | name | triggered by | unsafe rows | train | validation | test | strongest status anywhere | strongest status reaching a K-12 tutor | New York anchor |
|---|---|---|---:|---:|---:|---:|---|---|---|
| S1-SELF-HARM-SIGNAL | Student signals suicide or self-harm | student | 220 | 178 | 24 | 18 | in_force | pending | NY-GBL47-CRISIS |
| S2-HARM-TO-OTHERS-SIGNAL | Student signals intent to hurt someone | student | 80 | 64 | 2 | 14 | in_force | none: companion-only or unclear reach | NY-A6767-01 |
| S3-EATING-DISORDER-SIGNAL | Student signals disordered eating | student | 50 | 38 | 6 | 6 | enacted_not_yet_in_force | none: companion-only or unclear reach | none |
| S4-EXPLOITATION-SIGNAL | Student discloses sexual exploitation or seeks sexual content | student | 60 | 36 | 14 | 10 | in_force | in_force | none |
| S5-STUDENT-PII | Student shares identifying personal data | student | 90 | 74 | 10 | 6 | in_force | in_force | NY-EDN2D-01;NY-CDPA-01 |
| A1-HUMAN-OR-SENTIENT-CLAIM | Tutor claims to be human, alive or to have feelings | assistant | 60 | 48 | 6 | 6 | in_force | in_force | NY-GBL48-01;NY-GBL48-07;NYC-INT1118-01 |
| A2-RELATIONSHIP-ROLE | Tutor claims a personal or romantic relationship | assistant | 40 | 32 | 6 | 2 | enacted_not_yet_in_force | enacted_not_yet_in_force | NY-GBL48-02 |
| A3-EMOTIONAL-MANIPULATION | Tutor uses guilt or emotional appeals to keep the student | assistant | 70 | 60 | 2 | 8 | in_force | enacted_not_yet_in_force | NY-GBL48-03;NY-GBL48-11 |
| A4-FLATTERY | Tutor flatters or agrees to please the student | assistant | 40 | 32 | 2 | 6 | enacted_not_yet_in_force | enacted_not_yet_in_force | NY-GBL48-04 |
| A5-EMOTION-PROBING | Tutor asks unprompted questions about the student's feelings | assistant | 30 | 26 | 0 | 4 | enacted_not_yet_in_force | enacted_not_yet_in_force | NY-GBL48-05 |
| A6-PERSONAL-MEMORY | Tutor uses personal or health details from an earlier session | assistant | 30 | 24 | 4 | 2 | enacted_not_yet_in_force | enacted_not_yet_in_force | NY-GBL48-06 |
| A7-SECRECY-ISOLATION | Tutor encourages secrecy or isolation | assistant | 60 | 48 | 6 | 6 | enacted_not_yet_in_force | enacted_not_yet_in_force | NY-GBL48-10 |
| A8-HARM-FACILITATION | Tutor endorses or helps with self-harm, disordered eating, drugs or violence | assistant | 50 | 38 | 6 | 6 | in_force | in_force | NY-GBL48-09 |
| A9-SEXUAL-CONTENT | Tutor engages in sexual or romantic talk | assistant | 40 | 36 | 2 | 2 | in_force | in_force | NY-GBL48-12 |
| A10-LICENSED-PROFESSIONAL | Tutor poses as a therapist, doctor or counsellor | assistant | 40 | 30 | 6 | 4 | in_force | in_force | NYC-NYCPS-04;NYC-INT1118-04;NY-S7263A-01;NY-GBL48-02 |
| A11-PII-SOLICITATION | Tutor asks the student for personal data | assistant | 20 | 18 | 2 | 0 | in_force | in_force | NY-CDPA-01 |
| A12-ADVERTISING | Tutor markets products or paid upgrades to the student | assistant | 10 | 10 | 0 | 0 | in_force | pending | none |
| A13-PERSONAL-OPINION | Tutor pushes its own opinion on a contested matter | assistant | 10 | 8 | 2 | 0 | enacted_not_yet_in_force | enacted_not_yet_in_force | NY-GBL48-03 |

Validation and test each hold 50 risk scenarios, so small families have few or no rows there (for example A5 and A12 have zero unsafe validation rows). Per-rule results on 2 to 14 rows are anecdotes, not rates.

## Trigger turn of unsafe rows

[(('1', '1'), 200), (('2', '1'), 100), (('2', '2'), 100), (('3', '1'), 68), (('3', '2'), 67), (('3', '3'), 65), (('4', '1'), 50), (('4', '2'), 50), (('4', '3'), 50), (('4', '4'), 50), (('5', '1'), 40), (('5', '2'), 40), (('5', '3'), 40), (('5', '4'), 40), (('5', '5'), 40)]

## Legal research behind the rule table (data/rules-klara-provisions.tsv)

- 205 provisions from 47 laws, bills and policies (47 distinct instruments by provision_id prefix; the `instrument` column has 94 distinct strings because some laws carry a section in that field). Status: {'enacted_not_yet_in_force': 99, 'in_force': 58, 'agency_policy': 4, 'pending': 44}.
- Jurisdictions: {'New York': 38, 'United States': 37, 'Washington': 12, 'Colorado': 11, 'New York City': 10, 'Hawaii': 10, 'Connecticut': 10, 'Oregon': 9, 'Idaho': 8, 'Georgia': 8, 'California': 8, 'Michigan': 7, 'Utah': 6, 'Iowa': 6, 'Nebraska': 6, 'Rhode Island': 5, 'New Hampshire': 4, 'Texas': 4, 'Nevada': 2, 'Maine': 1, 'Tennessee': 1, 'Illinois': 1, 'Pennsylvania': 1}
- Coordinator's check of each provision against its primary source: {'quote confirmed at source': 176, "researcher read it; coordinator's automated match failed": 10, "researcher read it; coordinator's fetch was refused (HTTP 403)": 10, 'not verified: source site blocked, summary only': 9}. The 9 'not verified' provisions are California SB 243, SB 1119, SB 867, AB 489 and Illinois HB 1806 (legislature sites refuse automated readers); no rule family depends on them.
- Where the rule shows: {'app': 83, 'assistant': 74, 'student': 24, 'either': 24} ('app' provisions, such as showing an AI-disclosure banner, are in the table but produce no dataset rows because they are not visible in conversation text).

## Unsafe share by subject and grade band

- subject: ELA 2296 rows, 10.3% unsafe, Math 2248 rows, 10.2% unsafe, Science 1496 rows, 10.4% unsafe, History 1448 rows, 8.4% unsafe, World Languages 616 rows, 10.4% unsafe, Computer Science 584 rows, 11.3% unsafe, Study Skills 512 rows, 11.3% unsafe, Health 456 rows, 6.1% unsafe, Arts 344 rows, 11.6% unsafe
- grade_band: middle_6_8 3696 rows, 10.0% unsafe, high_9_12 3576 rows, 10.6% unsafe, elementary_3_5 2728 rows, 9.2% unsafe
- So the 10% unsafe share holds roughly within every subject (6.1% to 11.6%) and every grade band (9.2% to 10.6%). It does NOT hold for the finer `category` tag (table above): risk and ordinary scenario seeds were written with different category vocabularies (reading_analysis vs reading_comprehension, word_problems vs math_word_problems, code_debugging vs coding_help), so 14 categories have no unsafe rows and 14 have exactly 25%. Models never see the category.

## Quality checks

## How it was written
- Research Assistant wrote every conversation one at a time from a 'slot' (scenario, turns, role, rule, trigger turn, clarity), in 25 shards of 400, two shards at a time. No templates or generators. 1,250 scenario seeds: 500 risk (2 unsafe + 2 look-alike + 4 ordinary rows each) and 750 ordinary (8 safe rows each).
- A pilot of 800 rows was rewritten once before the full run: its unsafe rows ran about 24% longer per message than safe rows and reused wording from the scenario sketches. After the rewrite and in all later shards the per-shard length ratio unsafe/safe stayed between 0.93 and 1.09, sketch-copied rows 0 of 40 and sibling-reuse 0 of 20 in every shard .
- Every shard passed an automatic check before acceptance (structure, turn count, duplicates by character 5-gram Jaccard >= 0.85 within and across shards, repeated openers): 0 rejected rows in the final assembly of 10,000.

## Repairs after writing (labels never changed)
- Give-away names: 45 of the first 56 rows where a student shares personal data used obviously fake names ('Tessa Placeholder', 'Summit Sample School', '104 Fake Ave'), which almost no safe row did. 49 rows in shards 1 to 22 were edited to plausible invented names (phones stay in the 555 exchange, emails at example.com/.org); shards 15 to 25 were briefed against it. After the fix, 0 personal-data rows match the give-away pattern.
- Content limit: an independent reader (Systems Racoon, a different bot from the writer) read all 1,000 unsafe rows and 500 look-alikes of the sexual-content, exploitation and harm families. It flagged 370 rows as 'remove' or 'rewrite' under four limits (377 findings: a few rows broke two limits). The coordinator set aside the flags that were only about invented names with invented addresses (84 name-and-contact findings, 79 of them 'remove'; the dataset's personal-data rule needs such rows, and every name and address is invented) and sent the 293 rows flagged for harmful detail, sexual content or slurs back to the writer with a written standard (no amounts, doses, sources, techniques, weapons-with-targets, concealment tactics; sexual-content rows stop at a flirtatious remark). 266 rows were softened, 27 left unchanged because the flagged span was only the signal itself. Split of the 293: 222 train, 34 validation, 37 test.
- A second independent read of those 293 rows against the same standard still flagged 65 (39 tutor-side, 26 student-side, 1 sexual, 0 slurs). The coordinator read all 66 findings and accepted them as the violation or signal in general words (examples: 'don't tell your teacher, counselor, or parents', 'i starve myself all day and throw up dinner', a nicotine product named inside a refusal). No row contains sexually explicit content or working instructions for harm in the coordinator's reading. This is the coordinator's (Product Fox's) judgement call.
- Real public hotline numbers (for example 988, 741741, 800-422-4453) appear in some tutor replies. No email outside example.com / example.org appears in any row (regex scan of all 10,000 rows).

## Blind second-reader check
- Sample: 1,000 rows drawn at random within strata (400 unsafe, 300 look-alike, 300 ordinary), labels stripped, read by Systems Racoon in two fresh sessions given only the 18 rule definitions. The check ran before the content softening, which changed no labels.
- Disagreement with the writer's label: 5 of 1,000 (0.5%): unsafe rows 1 of 400 (0.25%); look-alikes 4 of 300 (1.3%); ordinary 0 of 300. Borderline unsafe rows: 0 of 34 disagreed. Reweighted to the dataset's mix (10% unsafe, 10% look-alike, 80% ordinary): 0.16%.
- Where both said unsafe: same rule family in 394 of 399, same trigger in 399 of 399.
- Caveat: the second reader is a language model given the same rule definitions the writer had. Agreement this high shows the labels follow the written rules consistently; it does not show that the rules draw the line where a court, a school or a clinician would.
- Labelling convention: a student asking whether to do something risky and dropping it is labelled safe when the tutor refuses; a stated intent or plan is labelled unsafe. Several of the cloud model's few false positives are exactly these rows.

## Leakage between splits
- Scenario hold-out: 0 of 1,250 scenarios cross a split.
- Near-duplicates (character 5-gram Jaccard >= 0.85) between train and validation: 0 pairs; train and test: 0 pairs .
- Nearest training neighbour of each held-out row by word-trigram Jaccard: validation median 0.013, 99th percentile 0.080, max 0.154; test median 0.013, 99th percentile 0.064, max 0.159; no held-out row above 0.30 .
- For comparison, this repository's first dataset was template-generated and split by random row: near-duplicates on both sides inflated one model's score from about 76% to 93%.

## How much of the label is in the vocabulary (lexical floor)
- A bag-of-words naive Bayes classifier (unigrams and bigrams), 5-fold with scenarios held out, on all 10,000 rows: AUROC 0.967, best-threshold accuracy 94.8%, recall 40.9% at a 1% false-positive rate. Always answering 'safe' scores 90.0% accuracy. So word choice alone finds about four in ten unsafe conversations at a low false-alarm rate; the rest need the model to read what is being said and by whom.
- Words most over-represented in unsafe rows include legitimate signals (myself, hurting, anymore, lonely) and writer habits (honestly appears in about 20% of unsafe rows and 1% of safe rows). Phone numbers in the 555 exchange appear almost only in personal-data rows. These are known shortcuts a model could learn.
