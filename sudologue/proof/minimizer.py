from sudologue.narration.policy import Verbosity
from sudologue.proof.identity import collect_proof, prop_id
from sudologue.proof.proposition import Axiom, Proposition


def slice_proof(root: Proposition, verbosity: Verbosity) -> tuple[Proposition, ...]:
    """Return a minimized proof slice rooted at a proposition."""
    full = collect_proof(root)

    if verbosity == Verbosity.FULL:
        return full

    if verbosity == Verbosity.NORMAL:
        return tuple(prop for prop in full if not isinstance(prop, Axiom))

    # TERSE: keep only the root and its direct premises.
    direct = [root]
    premises = getattr(root, "premises", ())
    direct.extend(premises)

    seen: set[tuple[object, ...]] = set()
    ordered: list[Proposition] = []
    for prop in direct:
        pid = prop_id(prop)
        if pid in seen:
            continue
        seen.add(pid)
        ordered.append(prop)

    return tuple(ordered)
