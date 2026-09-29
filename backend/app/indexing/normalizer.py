import re
from html import unescape
from typing import List

class TextNormalizer:
    """
    Standard Text Normalizer for the Vyrank IR System.
    Provides consistent tokenization and normalization for both
    indexing documents and processing search queries.
    """
    def __init__(self):
        # Basic punctuation regex to keep alphanumeric characters
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        self.html_pattern = re.compile(r"<[^>]*>")
        self.stop_words = {"a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "were", "with"}

    def process(self, text: str) -> List[str]:
        """
        Normalizes input text and splits it into a list of tokens.

        Args:
            text (str): The raw input string.

        Returns:
            List[str]: A list of normalized tokens.
        """
        if not text:
            return []

        # 1. Case folding (Lowercasing)
        text = unescape(self.html_pattern.sub(" ", text)).casefold()

        # 2. Remove punctuation
        text = self.punctuation_pattern.sub(' ', text)

        # 3. Tokenize by whitespace
        tokens = text.split()

        return [token for token in tokens if token not in self.stop_words]
