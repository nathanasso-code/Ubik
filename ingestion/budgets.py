"""Provider-agnostic acquisition budget and run accounting.

This module has no dependency on editorial selection or cluster processing.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SourceBudget:
    source_id: str
    max_requests: int
    max_observations: int
    requests: int = 0
    observations: int = 0
    errors: int = 0
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        if not self.source_id or type(self.max_requests) is not int or self.max_requests < 0:
            raise ValueError("Invalid request budget")
        if type(self.max_observations) is not int or self.max_observations < 0:
            raise ValueError("Invalid observation budget")

    def may_request(self):
        return self.requests < self.max_requests and self.observations < self.max_observations

    def record_request(self):
        if not self.may_request():
            raise RuntimeError("Source budget exhausted")
        self.requests += 1

    def record_result(self, count):
        if type(count) is not int or count < 0:
            raise ValueError("Invalid observation count")
        if self.observations + count > self.max_observations:
            raise RuntimeError("Observation budget exceeded")
        self.observations += count

    def record_error(self):
        self.errors += 1

    def report(self):
        return {
            "source_id": self.source_id,
            "started_at": self.started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "requests": self.requests,
            "observations": self.observations,
            "errors": self.errors,
            "max_requests": self.max_requests,
            "max_observations": self.max_observations,
            "exhausted": not self.may_request(),
            "editorial_decisions": 0,
        }
