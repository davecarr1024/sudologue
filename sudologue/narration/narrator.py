from typing import Protocol

from sudologue.inference.solve_result import SolveResult, TraceStep


class Narrator(Protocol):
    """Renders a solve trace into human-readable text."""

    def narrate(self, result: SolveResult) -> str: ...
    def narrate_step(self, step: TraceStep, step_number: int) -> str: ...


class DefaultNarrator:
    """Terse narrator that renders evidence descriptions directly."""

    def narrate(self, result: SolveResult) -> str:
        lines: list[str] = []
        lines.append(str(result.initial))
        lines.append("")
        for i, step in enumerate(result.steps, 1):
            lines.append(self.narrate_step(step, i))
        lines.append("")
        if result.diagnosis:
            lines.append(f"Stuck: {result.diagnosis}")
        else:
            lines.append(f"Solved in {len(result.steps)} steps.")
        return "\n".join(lines)

    def narrate_step(self, step: TraceStep, step_number: int) -> str:
        inf = step.inference
        return f"Step {step_number}: [{inf.rule}] {inf.evidence.description}"
