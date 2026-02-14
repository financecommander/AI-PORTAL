"""Tests for chat/search.py — conversation search."""

import pytest

from chat.search import search_history


class TestSearchHistory:
    def test_basic_match(self):
        history = [
            {"role": "user", "content": "What is revenue?"},
            {"role": "assistant", "content": "Revenue is income from operations."},
        ]
        results = search_history(history, "revenue")
        assert len(results) == 2

    def test_case_insensitive(self):
        history = [
            {"role": "user", "content": "HELLO WORLD"},
            {"role": "assistant", "content": "hello there"},
        ]
        results = search_history(history, "hello")
        assert len(results) == 2

    def test_no_match(self):
        history = [
            {"role": "user", "content": "What is GDP?"},
            {"role": "assistant", "content": "Gross Domestic Product."},
        ]
        results = search_history(history, "inflation")
        assert len(results) == 0

    def test_empty_query(self):
        history = [{"role": "user", "content": "something"}]
        results = search_history(history, "")
        assert results == []

    def test_whitespace_only_query(self):
        history = [{"role": "user", "content": "something"}]
        results = search_history(history, "   ")
        assert results == []

    def test_empty_history(self):
        results = search_history([], "query")
        assert results == []

    def test_max_results(self):
        history = [
            {"role": "user", "content": f"message {i}"}
            for i in range(20)
        ]
        results = search_history(history, "message", max_results=5)
        assert len(results) == 5

    def test_most_recent_first(self):
        history = [
            {"role": "user", "content": "first mention of finance"},
            {"role": "user", "content": "second mention of finance"},
            {"role": "user", "content": "third mention of finance"},
        ]
        results = search_history(history, "finance")
        assert results[0]["match_index"] == 2  # Most recent
        assert results[1]["match_index"] == 1
        assert results[2]["match_index"] == 0  # Oldest

    def test_match_index_correct(self):
        history = [
            {"role": "user", "content": "no match here"},
            {"role": "assistant", "content": "target message"},
            {"role": "user", "content": "no match again"},
        ]
        results = search_history(history, "target")
        assert len(results) == 1
        assert results[0]["match_index"] == 1

    def test_preserves_message_fields(self):
        history = [
            {"role": "assistant", "content": "The answer is 42."},
        ]
        results = search_history(history, "answer")
        assert results[0]["role"] == "assistant"
        assert results[0]["content"] == "The answer is 42."
        assert "match_index" in results[0]

    def test_partial_match(self):
        history = [
            {"role": "user", "content": "What about cryptocurrency?"},
        ]
        results = search_history(history, "crypto")
        assert len(results) == 1

    def test_missing_content_key(self):
        history = [
            {"role": "user"},  # No content key
        ]
        results = search_history(history, "anything")
        assert len(results) == 0

    def test_max_results_one(self):
        history = [
            {"role": "user", "content": "match A"},
            {"role": "user", "content": "match B"},
        ]
        results = search_history(history, "match", max_results=1)
        assert len(results) == 1
        assert results[0]["content"] == "match B"  # Most recent
