"""Port defining the contract for AI-assisted operational reasoning."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from m3d.domain.evidence import Evidence
from m3d.domain.hypothesis import Hypothesis
from m3d.domain.investigation import Investigation


class ReasoningProvider(ABC):
    """Abstract interface for AI-assisted operational reasoning."""

    @abstractmethod
    def generate_hypotheses(
        self,
        investigation: Investigation,
        evidence: Sequence[Evidence],
    ) -> list[Hypothesis]:
        """Generate possible explanations from the available evidence."""
        raise NotImplementedError

    @abstractmethod
    def evaluate_evidence(
        self,
        investigation: Investigation,
        hypothesis: Hypothesis,
        evidence: Sequence[Evidence],
    ) -> float:
        """Evaluate how strongly the evidence supports a hypothesis."""
        raise NotImplementedError

    @abstractmethod
    def propose_investigation_step(
        self,
        investigation: Investigation,
        hypothesis: Hypothesis,
        evidence: Sequence[Evidence],
    ) -> str:
        """Propose the next investigation step."""
        raise NotImplementedError

    @abstractmethod
    def evaluate_result(
        self,
        investigation: Investigation,
        hypothesis: Hypothesis,
        evidence: Sequence[Evidence],
    ) -> str:
        """Evaluate the result of testing a hypothesis."""
        raise NotImplementedError

    @abstractmethod
    def generate_conclusion(
        self,
        investigation: Investigation,
        evidence: Sequence[Evidence],
        hypotheses: Sequence[Hypothesis],
    ) -> str:
        """Generate a conclusion from the investigation findings."""
        raise NotImplementedError
