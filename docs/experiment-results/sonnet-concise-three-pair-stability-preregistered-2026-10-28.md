# Sonnet concise: preregistered three-pair stability adjudication (2026-10-28)

## Frozen scope
Original v5 Sonnet model and judge PROMPT unchanged. Rejudge only these three pairs from frozen artifacts 12719538526 and 12725256478, against concise run artifact 12777392635:
1. S387:e2 / S465:e2: original uncertain, concise distinct.
2. S188:e2 / S383:e2: original equivalent, concise uncertain.
3. S389:e4 / S408:e7: original uncertain, concise distinct.

No extraction, retrieval, composer or gold-reference changes. Preserve original reasoning configuration. Record response and actual cost for each. No early stopping or selective reporting. Compare exact decision and direction, then independently adjudicate semantics. Do not declare a format effect solely from one repeat.

## Interpretations frozen before rerun
- Pair 2: if original Sonnet switches to uncertain, classify as possible judge instability, not proven concise-format regression. If it remains equivalent, evidence for format-associated difference, subject to repeated-trial uncertainty.
- Pairs 1 and 3: if original Sonnet stays uncertain, evidence consistent with concise-format drift toward distinct; not proof of causality.
- Distinct requires positive evidence of difference; absence of identity evidence alone is insufficient. This is an *evaluation criterion*, not a change to the rerun prompt.
- Pair 1 is provisionally considered a legitimate A/B separation, pending extraction-blind event alignment.
- Pair 2 loses expected equivalence but may not add a second weight-2 split if the same incident was already split; possible extra card-level weight-1 error. No double counting.
- Pair 3's underlying reference is provisionally indeterminate; the concise rationale may hallucinate a supply agreement. Confirm against frozen extraction.
- Do not promote concise Sonnet from these three results alone. If a new prompt is needed, preregister and test it as a separate version.

## Costs and optimization
Frozen concise judge cost $0.394232, frozen extraction $0.149988, total $0.544220 vs v4 $0.335854. Cache was not used; batch not used. Provider capabilities and effective prompt-cache thresholds must be verified before claiming savings. Do not assume hypothetical batch pricing is actual cost.

## Branch
Only experiment/taxonomy-fewshot-pilot; main unchanged.
