# Roadmap

## Completed

- Core model: cells, houses, board, validation, parsing
- Proof propositions: axioms, eliminations, domain lemmas, theorems
- Proof engine with derived views (candidates/domains/ranges)
- Solver loop, CLI, and 4x4 + 9x9 puzzle coverage
- Naked single and hidden single with range-first narration
- Rule split: elimination rules (derive facts) vs selection rules (place values)

## Remaining Work (Phased Plan)

Each phase is shippable with full tests and its own commit series.

### Phase 1: Proof Identity + Naming Clarity

Goal: make proof graph tooling-ready without changing solver behavior.

- [x] Add stable proposition IDs: hashable by `(type, conclusion fields)`
- [x] Add proof index utilities for de-duplication/slicing
- [x] Optional rename path: `Elimination` -> `NotCandidate` (type alias + doc update)
- [x] Tests: ID stability, de-duplication across derivations, backward traversal

### Phase 2: Range Lemmas + Candidate Promotion

Goal: expose range-first reasoning as first-class proof objects.

- [x] Introduce `RangeLemma(house, value, cells, premises)`
- [x] Define premises for RangeLemma based on NotCandidate facts
- [x] Optional explicit `Candidate` nodes (derived or computed)
- [x] Update narrator to surface RangeLemma in hidden single explanations
- [x] Tests: range lemma derivation, premise coverage, hidden single proof chains

### Phase 3: Proof Minimization + Narration Policies

Goal: make explanations minimal, policy-driven, and stable.

- [x] Implement backward slicing over the proof DAG (terse/normal/full)
- [x] Add narration policies (range-first vs domain-first; verbosity modes)
- [x] Add proof scoring hooks for choosing among theorems
- [x] Tests: slicing removes redundant premises without breaking validity

### Phase 4: Mid-Level Techniques

Goal: progress beyond singles while preserving proof structure.

- [x] Pointing pairs / box-line reduction (range-first)
- [ ] Add 9x9 puzzles that require these rules
- [x] Tests: rule-specific derivations

### Phase 5: Structure Lemmas

Goal: represent multi-digit logic as structure, then emit eliminations from it.

- [ ] Introduce `Pair(house, digits, cells)` (and later triple/quad) as a structure lemma
- [ ] Hidden pair as two-step: structure observation + digit-aligned eliminations
- [ ] Narration: show structure nodes in full mode, hide in terse

### Phase 6: Advanced Fish

Goal: scalable pattern rules with clean proofs.

- X-Wing (row/column range intersections)
- Swordfish (generalized fish patterns)
- Stress-test narration for complex premises
- Tests: targeted 9x9 fixtures + proof chain integrity
