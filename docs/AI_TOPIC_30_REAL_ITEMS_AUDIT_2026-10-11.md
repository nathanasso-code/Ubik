# Ubik — First concrete 30-document AI topic audit (2026-10-11)

Source: successful live GitHub Actions run https://github.com/nathanasso-code/Ubik/actions/runs/38122381477 ; step "Print compact topic candidates for reviewer inspection". 105 candidate documents, 30 selected, **0 suggested same-event pairs** under the current title-token rule. This is title-and-source-metadata triage, **not** full-article verification or editorial publication approval.

## Observed source-level cases

- arXiv cs.AI: "On the estimation and validity of AI time horizons---a statistical look at the METR plot" (https://arxiv.org/abs/2610.12466v1). Potentially valuable primary research; extract research question, methodology and limitations from abstract before ranking.
- BBC: "Rogue Anthropic AI agent gave police fake tip in unsolved murder case" (https://www.bbc.co.uk/news/articles/cqkg50j1yd5lo?at_medium=RSS&at_campaign=rss). Potentially relevant real-world AI safety incident; verify article, date and independent sourcing.
- Normal Tech: "AI existential risk probabilities are (still) too unreliable to inform policy" (https://www.normaltech.ai/p/p-doom). Analytical argument, not necessarily an event; keep standalone unless an exact same claim/event is covered.
- OpenAI: "Asana cuts model costs 76x in browser tests with GPT-6.1 Sol" (https://openai.com/index/asana-browser-agent). First-party case study and attributed performance claim; avoid treating as independent verification.
- Simon Willison: "Python 3.15.0 added to actions/python-versions" (https://simonwillison.net/2026/Oct/10/python-actions/). Likely false-positive AI relevance due to broad feed description or term matching; should be reviewed/excluded from this topic.
- arXiv cs.CL: "SpaceCast-Bench: Evaluating Predictive Spatial Reasoning in Vision-Language Models" (https://arxiv.org/abs/2610.12402v1). Standalone primary research candidate.
- Latent Space: "[AINews] Claude Haiku 5.5 — better than GPT-6 Luna at the same pricing" (https://www.latent.space/p/ainews-claude-haiku-55-better-than). Possible release/comparison story; compare to primary vendor release, distinguish comparison opinion from announcement.
- Latent Space: "[AINews] Quasi-Riemann-Hypothesis: OpenAI publishes 722 math papers solving 90 of the top 500 open math problems..." (https://www.latent.space/p/ainews-quasi-riemann-hypothesis-openai). Extraordinary claim; do not amplify as verified without checking primary evidence.
- Simon Willison: "A new feature for my blog, built using my voice" (https://simonwillison.net/2026/Oct/9/built-using-my-voice/). Unclear AI topic relevance from title alone.

## Diagnosis and priorities

1. **Selection false positives**: matching AI-related words in generic feed descriptions, or generic terms such as `api` and `research`, can mislabel irrelevant material. Introduce evidence-based per-document topic labels and abstention, not blind publisher priors.
2. **Topic coverage**: 30 sampled documents from 105 candidates cannot establish event clustering quality. Search the entire candidate set before imposing a 30-card display cap.
3. **Event vs argument**: studies, opinions, announcements and incidents have different grouping criteria. Group only the same bounded event or documented research result; don't merge all AI safety pieces.
4. **Source independence**: a company's own case study is useful, but not independently corroborated by reposts. Give primary research and substantive expert arguments an opportunity to surface as standalone.
5. **No reliable trend**: a single collection snapshot cannot establish momentum. Need repeated snapshots, unique-origin growth and time normalization.
6. **Editorial experiment**: build a compact review table with decision `include / exclude / uncertain`, content type, topical area, claim/message, and reason. Do not fabricate full-text assessment.

The next useful implementation is full-candidate same-event candidate retrieval with strict review status, plus a review table grounded in actual article metadata. No automatic publication, debate or nucleus activation.
