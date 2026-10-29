"""Preflight cost estimates: refuse a paid stage before the first call when its estimate exceeds the budget.

Unit costs are measured, not list prices: Ukraine v5.1 judges (126 pairs) and the 2026-10-29 corpus probe.
"""
UNIT_COST = {
    "judge:sonnet": 0.0041,          # USD per pair, Ukraine v5.1 Sonnet 5.5 arm (0.5146 / 126)
    "judge:deepseek": 0.0002,        # USD per pair, Ukraine v5.1 DeepSeek V4.1 Flash arm (0.0248 / 126)
    # Extraction pilot 2026-10-29: Sonnet 0.0299 USD per article (~5400 input chars, ~2300 output tokens);
    # output tokens dominate, so the earlier 0.0031/kchar estimate (derived from the probe total) was too low.
    "extract:sonnet_per_kchar": 0.0055,
    "extract:sonnet_per_call": 0.0,
    "extract:deepseek_per_article_full": 0.0026,   # same pilot, D-full
    "extract:deepseek_per_article_lede": 0.0013,   # same pilot, D-lede (~1500 chars)
}
SAFETY = 1.25


def extraction_estimate(chars, calls):
    return SAFETY * (UNIT_COST["extract:sonnet_per_kchar"] * chars / 1000 + UNIT_COST["extract:sonnet_per_call"] * calls)


def cascade_estimate(pairs, escalation_rate=0.15):
    """DeepSeek judges every pair; Sonnet re-judges those DeepSeek did not call distinct (about 24% on Ukraine)."""
    return SAFETY * pairs * (UNIT_COST["judge:deepseek"] + escalation_rate * UNIT_COST["judge:sonnet"])


class OverBudget(RuntimeError):
    pass


def preflight(stage, estimate_usd, budget_usd, log):
    log.append({"stage": stage, "estimate_usd": round(estimate_usd, 4), "budget_usd": budget_usd})
    if estimate_usd > budget_usd:
        raise OverBudget(f"{stage}: estimated {estimate_usd:.3f} USD exceeds the budget of {budget_usd:.2f} USD; nothing was called")
