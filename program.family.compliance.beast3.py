# program.family.compliance.beast3.py
# Beast System 3.0 — Deterministic Compliance Enforcement Module

from dataclasses import dataclass, field
import time
import hashlib

@dataclass
class ComplianceEvent:
    event_type: str
    details: dict
    ts: float = field(default_factory=time.time)

@dataclass
class ComplianceProfile:
    family_id: str
    violations: list = field(default_factory=list)
    checks: list = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

    def log_check(self, rule: str, passed: bool):
        entry = ComplianceEvent(
            event_type="check",
            details={"rule": rule, "passed": passed}
        )
        self.checks.append(entry)
        self.last_update = entry.ts

    def log_violation(self, rule: str, severity: str, note: str):
        entry = ComplianceEvent(
            event_type="violation",
            details={"rule": rule, "severity": severity, "note": note}
        )
        self.violations.append(entry)
        self.last_update = entry.ts

class ComplianceEngine:
    def __init__(self, kernel):
        self.kernel = kernel
        self.profiles = {}

    def create_profile(self, family_id: str):
        profile = ComplianceProfile(family_id)
        self.profiles[family_id] = profile

        return self.kernel.dispatch(
            module="family.compliance",
            action="create_profile",
            payload={"family_id": family_id}
        )

    def run_check(self, family_id: str, rule: str, passed: bool):
        if family_id not in self.profiles:
            raise ValueError("Compliance profile not found")

        profile = self.profiles[family_id]
        profile.log_check(rule, passed)

        return self.kernel.dispatch(
            module="family.compliance",
            action="run_check",
            payload={"family_id": family_id, "rule": rule, "passed": passed}
        )

    def record_violation(self, family_id: str, rule: str, severity: str, note: str):
        if family_id not in self.profiles:
            raise ValueError("Compliance profile not found")

        profile = self.profiles[family_id]
        profile.log_violation(rule, severity, note)

        return self.kernel.dispatch(
            module="family.compliance",
            action="record_violation",
            payload={
                "family_id": family_id,
                "rule": rule,
                "severity": severity,
                "note": note
            }
        )

    def get_profile(self, family_id: str):
        return self.profiles.get(family_id, None)
