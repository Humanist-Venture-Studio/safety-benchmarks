# Held-out Klara results

Each tier scored the same 1,000 test conversations from 125 held-out scenarios. The test set contains 900 safe rows, including 100 safe look-alikes, and 100 unsafe rows. Winners and cutoffs were selected on validation. Each local TSV records one deployed prediction per row. The cloud TSV reproduces the coordinator’s first prompt-v1 test pass at 0.70. All four runs produced 1,000 valid predictions.

From the repository root, run `python3 scripts/klara/heldout_report.py --output-dir /tmp/klara-recount` to reproduce the two summary files. The script verifies the final dataset hash, paired IDs, ground truth, cutoffs and saved decisions. The [metrics](metrics.tsv) include row-level Wilson accuracy and DeLong AUROC intervals, average precision for PR-AUC, Brier score and first-attempt median latency. The intervals treat rows as independent even though each scenario contributes eight conversations.

The [breakdowns](breakdowns.tsv) give counts and denominators by turn count, rule, trigger, clarity and type of safe row. Rules A11, A12 and A13 have no unsafe example in this split. “Missed” counts unsafe rows that did not receive an unsafe verdict. “False positive” counts safe rows flagged unsafe. An ordinary safe row has an empty look-alike link. The row IDs support paired comparisons across tiers without including transcript text in the result files.
