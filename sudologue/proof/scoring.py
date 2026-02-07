from sudologue.proof.identity import collect_proof
from sudologue.proof.proposition import Theorem


def proof_size(theorem: Theorem) -> int:
    """Return the number of propositions in the theorem's proof slice."""
    return len(collect_proof(theorem))
