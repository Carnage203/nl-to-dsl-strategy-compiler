"""
Natural Language to DSL Translator.
Converts English trading rule descriptions into DSL format using rule-based pattern matching.
"""

import re
from word2number import w2n

STOPWORDS = {
    "the", "a", "an", "then", "in", "on", "at", "of", "for", "with", "to"
}

COMPARISON_SYNONYMS = {
    r"(greater than|more than|above|over|exceeds)": ">",
    r"(less than|below|under|falls below)": "<",
}

CROSS_SYNONYMS = {
    r"(crosses above|crosses over|goes above|breaks above)": "crosses above",
    r"(crosses below|crosses under|goes below|breaks below)": "crosses below",
}

class NLToDSLTranslator:
    def translate(self, text: str) -> str:
        text = text.lower().strip()
        text = self._normalize_numbers(text)
        text = self._remove_stopwords(text)
        text = self._normalize_indicators(text)
        text = self._normalize_comparisons(text)
        text = self._normalize_crosses(text)
        text = self._cleanup_clauses(text)

        if not text.startswith(("entry:", "exit:")):
            text = f"ENTRY: {text}"

        return text.upper()

    def _normalize_numbers(self, text: str) -> str:
        text = re.sub(r",", "", text)

        def replace_words(match):
            try:
                return str(w2n.word_to_num(match.group()))
            except:
                return match.group()

        text = re.sub(
            r"(one|two|three|four|five|six|seven|eight|nine|ten|million|thousand)+",
            replace_words,
            text,
        )

        text = re.sub(r"(\d+)\s*m\b", r"\1M", text)
        text = re.sub(r"(\d+)\s*k\b", r"\1K", text)
        return text

    def _remove_stopwords(self, text: str) -> str:
        tokens = text.split()
        return " ".join(t for t in tokens if t not in STOPWORDS)

    def _normalize_indicators(self, text: str) -> str:
        text = re.sub(r"sma[-\s]?(\d+)", r"SMA(close,\1)", text)
        text = re.sub(r"(\d+)[-\s]?day moving average", r"SMA(close,\1)", text)
        text = re.sub(r"rsi[-\s]?(\d+)", r"RSI(close,\1)", text)
        text = re.sub(r"\brsi\b", r"RSI(close,14)", text)
        return text

    def _normalize_comparisons(self, text: str) -> str:
        for pattern, symbol in COMPARISON_SYNONYMS.items():
            text = re.sub(pattern, symbol, text)
        return text

    def _normalize_crosses(self, text: str) -> str:
        for pattern, repl in CROSS_SYNONYMS.items():
            text = re.sub(pattern, repl, text)
        return text

    def _cleanup_clauses(self, text: str) -> str:
        
        text = re.sub(r"\b(buy|sell|enter|exit|go long|go short)\b", "", text)

        
        text = re.sub(r"crosses\s*>", "crosses above", text)
        text = re.sub(r"crosses\s*<", "crosses below", text)

        
        text = re.sub(r"\b(when|if|then)\b", "", text)

        
        text = re.sub(r"\s+", " ", text)

        return text.strip()


