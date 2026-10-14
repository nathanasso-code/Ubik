# Ubik — pretrained semantic model comparison
Status: evaluation plan only. No measured improvement yet.

## Why
Multilingual NLI neutral does not imply different events. Contradictions can represent compatible temporal stages. Event identity, claim relationship and factual truth require separate evaluation.

## Candidate components
- BERTopic multilingual: broad topic discovery, not same-event clustering. https://github.com/MaartenGr/BERTopic
- Existing multilingual E5: candidate retrieval baseline.
- Qwen/Qwen3-Reranker-0.6B (Apache-2.0): multilingual pair reranking; scores are not factual verdicts. https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
- HerO 2: existing evidence retrieval and claim verification pipeline, to evaluate, not assume transferable. https://github.com/ssu-humane/HerO2
- AVeriTeC: evidence-based claim verification dataset and evaluation. https://fever.ai/2025/task.html

## Experiment A: same-event matching
Freeze >=200 source-linked documents and independently annotate >=100 candidate pairs, including multilingual positives, same-topic different-event negatives, and different temporal stages. Compare existing E5 with E5 plus Qwen reranker. Measure precision@k, recall@k, event-pair F1, false merges, latency, costs and per-language performance. No tuning on test split.

## Experiment B: evidence-based claim assessment
Compare existing NLI to HerO2-style retrieval, question generation and evidence-based verdicts on independently annotated claims. Evaluate factual verdict and adequacy of cited evidence jointly. Missing evidence means unknown, not false.

## Experiment C: grounded synthesis
Generate only from source-linked passages. Independently score attribution, factual fidelity, coverage and omission.

## Safety gates
No automatic merge until held-out pairwise evaluation demonstrates improvement with acceptable false merges. No automatic contradiction assertion from NLI. Record dataset snapshot, source dates, model version, prompts, reviewer provenance and inference costs. The current 24 unannotated pairs are triage, not accuracy evidence.
