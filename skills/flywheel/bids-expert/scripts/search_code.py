#!/usr/bin/env python3
"""Search the Flywheel code index — the depth layer for the bids-expert skill.

Loads references/flywheel/code-index/cards.jsonl, ranks cards against a query
with BM25, and prints the top matches with `path:line` and the real source.
Use this when the curated `references/flywheel/*.md` overviews don't answer a
technical question and you need the actual implementation or a real template
rule.

Identifiers are split (camelCase + snake_case) so a natural-language query like
"why is a file not recognized during matching" lines up with symbols like
`rule_matches` / `process_matching_templates`.

Usage:
    python search_code.py "intendedfor fieldmap resolver" [-k 5]
        [--repo bids-client] [--kind code|template-rule|template-def] [--full]
"""

import argparse
import json
import math
import re
import typing as t
from pathlib import Path

DEFAULT_CARDS = Path(__file__).resolve().parent.parent / "references" / "flywheel" / "code-index" / "cards.jsonl"
K1 = 1.5
B = 0.75
SNIPPET_LINES = 45


def tokenize(text: str) -> t.List[str]:
    """Lowercase tokens, splitting camelCase and snake_case into word parts."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    return re.findall(r"[a-z0-9]+", text.lower())


def card_tokens(card: dict) -> t.List[str]:
    """Field-boosted token list for a card (name/signature weighted higher)."""
    name = tokenize(card.get("name", ""))
    sig = tokenize(card.get("signature", ""))
    doc = tokenize(card.get("doc", ""))
    body = tokenize(card.get("text", ""))
    return name * 3 + sig * 2 + doc + body


class Bm25Index:
    """In-memory BM25 over the card corpus (built fresh per run — fast enough)."""

    def __init__(self, cards: t.List[dict]):
        """Tokenize every card and precompute document frequencies."""
        self.cards = cards
        self.docs = [card_tokens(c) for c in cards]
        self.dls = [len(d) for d in self.docs]
        self.avgdl = (sum(self.dls) / len(self.dls)) if self.dls else 0.0
        self.tfs = [self._term_freqs(d) for d in self.docs]
        self.df: t.Dict[str, int] = {}
        for tf in self.tfs:
            for term in tf:
                self.df[term] = self.df.get(term, 0) + 1
        self.n = len(cards)

    @staticmethod
    def _term_freqs(tokens: t.List[str]) -> t.Dict[str, int]:
        """Count term frequencies in one document."""
        freqs: t.Dict[str, int] = {}
        for tok in tokens:
            freqs[tok] = freqs.get(tok, 0) + 1
        return freqs

    def _idf(self, term: str) -> float:
        """BM25 idf for a term."""
        df = self.df.get(term, 0)
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def search(self, query: str, k: int, predicate: t.Callable[[dict], bool]) -> t.List[t.Tuple[float, dict]]:
        """Return the top-k (score, card) pairs matching predicate."""
        q_terms = tokenize(query)
        scored: t.List[t.Tuple[float, dict]] = []
        for i, card in enumerate(self.cards):
            if not predicate(card):
                continue
            score = self._score(i, q_terms)
            if score > 0:
                scored.append((score, card))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:k]

    def _score(self, doc_idx: int, q_terms: t.List[str]) -> float:
        """BM25 score of one document against the query terms."""
        tf = self.tfs[doc_idx]
        dl = self.dls[doc_idx]
        score = 0.0
        for term in q_terms:
            f = tf.get(term, 0)
            if not f:
                continue
            denom = f + K1 * (1 - B + B * dl / self.avgdl) if self.avgdl else f + K1
            score += self._idf(term) * (f * (K1 + 1)) / denom
        return score


def load_cards(path: Path) -> t.List[dict]:
    """Load cards.jsonl into a list of dicts."""
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def format_card(score: float, card: dict, full: bool) -> str:
    """Render one result: location, signature/name, doc, and source snippet."""
    loc = card["path"] + (f":{card['line']}" if "line" in card else "")
    header = f"[{score:.2f}] {card['kind']} · {card['repo']} · {loc}"
    title = card.get("name", "")
    doc = (card.get("doc", "") or "").strip().splitlines()
    doc_line = f"\n    {doc[0]}" if doc else ""
    text = card.get("text", "")
    if not full:
        body_lines = text.splitlines()
        if len(body_lines) > SNIPPET_LINES:
            text = "\n".join(body_lines[:SNIPPET_LINES]) + f"\n    … ({len(body_lines) - SNIPPET_LINES} more lines — use --full or open {loc})"
    return f"{header}\n  {title}{doc_line}\n\n{text}\n"


def main() -> None:
    """Parse args, search the index, print results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="search terms")
    parser.add_argument("-k", type=int, default=5, help="number of results (default 5)")
    parser.add_argument("--repo", help="filter by repo (bids-client / curate-bids / relabel-container)")
    parser.add_argument("--kind", help="filter by kind (code / template-rule / template-def)")
    parser.add_argument("--full", action="store_true", help="print full source, not a snippet")
    parser.add_argument("--cards", type=Path, default=DEFAULT_CARDS)
    args = parser.parse_args()

    cards = load_cards(args.cards)
    index = Bm25Index(cards)

    def predicate(card: dict) -> bool:
        if args.repo and card.get("repo") != args.repo:
            return False
        if args.kind and card.get("kind") != args.kind:
            return False
        return True

    results = index.search(args.query, args.k, predicate)
    if not results:
        print(f"No matches for: {args.query}")
        return
    print(f"Top {len(results)} for: {args.query}\n")
    for score, card in results:
        print(format_card(score, card, args.full))
        print("-" * 80)


if __name__ == "__main__":
    main()
