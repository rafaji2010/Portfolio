"""
core/trie.py
Trie implementation for autocomplete
"""

from __future__ import annotations
from typing import Dict, List, Optional


class TrieNode:
    """Node in a Trie."""

    def __init__(self) -> None:
        self.children: Dict[str, TrieNode] = {}
        self.is_end: bool = False


class Trie:
    """
    Trie data structure for efficient prefix search.

    Time: O(m) for insert, search, and starts_with where m = length of string
    Space: O(n * m) where n = number of strings, m = average length
    """

    def __init__(self) -> None:
        self.root = TrieNode()
        self._size: int = 0

    def insert(self, word: str) -> None:
        """
        Insert a word into the trie.

        Args:
            word: String to insert
        """
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        if not node.is_end:
            node.is_end = True
            self._size += 1

    def search(self, word: str) -> bool:
        """
        Check if a word exists in the trie.

        Args:
            word: String to search for

        Returns:
            True if word exists, False otherwise
        """
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def starts_with(self, prefix: str) -> List[str]:
        """
        Find all words that start with a given prefix.

        Args:
            prefix: Prefix to search for

        Returns:
            List of words starting with the prefix
        """
        results: List[str] = []

        # Navigate to the node at the end of the prefix
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # DFS to collect all words
        self._collect_words(node, prefix.lower(), results)
        return results

    def _collect_words(self, node: TrieNode, current: str, results: List[str]) -> None:
        """Helper to collect all words from a node."""
        if node.is_end:
            results.append(current)

        for char, child in node.children.items():
            self._collect_words(child, current + char, results)

    def delete(self, word: str) -> bool:
        """
        Delete a word from the trie.

        Args:
            word: Word to delete

        Returns:
            True if deleted, False if word not found
        """
        return self._delete_recursive(self.root, word.lower(), 0)

    def _delete_recursive(self, node: TrieNode, word: str, depth: int) -> bool:
        """Recursive delete helper."""
        if depth == len(word):
            if not node.is_end:
                return False
            node.is_end = False
            self._size -= 1
            return len(node.children) == 0

        char = word[depth]
        if char not in node.children:
            return False

        should_delete_child = self._delete_recursive(node.children[char], word, depth + 1)

        if should_delete_child:
            del node.children[char]
            return len(node.children) == 0 and not node.is_end

        return False

    def size(self) -> int:
        """Return number of words in trie."""
        return self._size

    def __len__(self) -> int:
        return self._size

    def __contains__(self, word: str) -> bool:
        return self.search(word)


if __name__ == "__main__":
    print("=== Trie Demo ===")

    trie = Trie()

    # Insert words
    words = ["apple", "app", "apricot", "banana", "bat", "ball", "cat"]
    for word in words:
        trie.insert(word)

    print(f"Trie size: {len(trie)}")

    # Search
    print(f"\nSearch 'apple': {trie.search('apple')}")
    print(f"Search 'app': {trie.search('app')}")
    print(f"Search 'ape': {trie.search('ape')}")

    # Autocomplete
    print(f"\nStarts with 'ap': {trie.starts_with('ap')}")
    print(f"Starts with 'ba': {trie.starts_with('ba')}")
    print(f"Starts with 'c': {trie.starts_with('c')}")
    print(f"Starts with 'z': {trie.starts_with('z')}")
