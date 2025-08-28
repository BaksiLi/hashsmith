#!/usr/bin/env python3
"""
Test cases for HashSmith transform behavior.

Tests the key feature that .alter() always includes original items
plus transformed versions.
"""

import sys
from pathlib import Path

import pytest

# Setup path to import from src
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from hashsmith.patterns.engine import P, PAnd, POr, Transform


class TestTransformBehavior:
    """Test the behavior of the .expand() method (inclusive)."""

    def test_single_transform_includes_original(self):
        """Test that single transform includes original + transformed."""
        pattern = P(["test"]).expand(Transform.UPPER)
        result = list(pattern.generate())

        expected = ["test", "TEST"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_multiple_items_with_transform(self):
        """Test multiple items each get original + transformed."""
        pattern = P(["hello", "world"]).expand(Transform.CAPITALIZE)
        result = list(pattern.generate())

        expected = ["hello", "Hello", "world", "World"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_multiple_transforms_no_duplicates(self):
        """Test multiple transforms do not create duplicates."""
        pattern = P(["test"]).expand(Transform.UPPER, Transform.LOWER)
        result = list(pattern.generate())

        # "test" -> LOWER -> "test" (duplicate of original)
        # "test" -> UPPER -> "TEST"
        expected = ["test", "TEST"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_lambda_transform_includes_original(self):
        """Test lambda transforms include original."""
        pattern = P(["hello"]).expand(lambda x: x + "!")
        result = list(pattern.generate())

        expected = ["hello", "hello!"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_mixed_transform_types(self):
        """Test mixing Transform enum and lambda functions."""
        pattern = P(["test"]).expand(Transform.UPPER, lambda x: x + "123")
        result = list(pattern.generate())

        expected = ["test", "TEST", "test123"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_no_transforms_returns_original(self):
        """Test that .expand() with no args returns original pattern."""
        p1 = P(["test"])
        p2 = p1.expand()
        assert p1 == p2

    def test_empty_alter_returns_original(self):
        """Passing no transforms should not change the pattern."""
        p1 = P(["test"])
        p2 = p1.expand()
        assert list(p1.generate()) == list(p2.generate())

    def test_chained_alters(self):
        """Test chaining multiple .expand() calls."""
        pattern = P(["hello"]).expand(Transform.UPPER).expand(lambda x: x + "!")
        result = list(pattern.generate())

        # Chained alters work like method chaining: each .expand() operates on
        # the results of the previous pattern, not just the original items
        expected = ["hello", "hello!", "HELLO", "HELLO!"]
        assert set(result) == set(
            expected
        ), f"Expected {set(expected)}, got {set(result)}"

    def test_leet_transform_includes_original(self):
        """Test leet transformations include original."""
        pattern = P(["password"]).expand(Transform.LEET_BASIC)
        result = list(pattern.generate())

        expected = ["password", "p@$$w0rd"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_numeric_transforms(self):
        """Test numeric zero-padding transforms."""
        pattern = P(["5", "42"]).expand(Transform.ZERO_PAD_2)
        result = list(pattern.generate())

        # "42" zero-padded to 2 digits is still "42", so duplicate is removed
        expected = ["5", "05", "42"]  # No duplicate "42"
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_case_sensitive_duplicates_avoided(self):
        """Test that case transforms avoid creating duplicates."""
        pattern = P(["HELLO"]).expand(Transform.UPPER, Transform.LOWER)
        result = list(pattern.generate())

        expected = ["HELLO", "hello"]  # UPPER of "HELLO" is duplicate
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"


class TestEstimateCount:
    """Test count estimation with transforms."""

    def test_estimate_with_no_transforms(self):
        """Test count estimation with no transforms."""
        pattern = P(["a", "b"])
        assert pattern.estimate_count() == 2

    def test_estimate_with_single_transform(self):
        """Test count estimation with single transform."""
        pattern = P(["a", "b"]).expand(Transform.UPPER)
        # 2 items * (1 original + 1 transform) = 4
        assert pattern.estimate_count() == 4

    def test_estimate_with_multiple_transforms(self):
        """Test count estimation with multiple transforms."""
        pattern = P(["test"]).expand(Transform.UPPER, Transform.LOWER)
        # 1 item * (1 original + 2 transforms) = 3
        assert pattern.estimate_count() == 3

    def test_estimate_with_lambda_transforms(self):
        """Test count estimation includes lambda transforms."""
        pattern = P(["hello"]).expand(lambda x: x + "!", lambda x: x[::-1])
        # 1 item * (1 original + 2 lambda transforms) = 3
        assert pattern.estimate_count() == 3


class TestCompositePatterns:
    """Test composite patterns involving transforms."""

    def test_pand_with_transforms(self):
        """Test PAnd patterns with transforms."""
        pattern = PAnd(
            P(["hello"]).expand(Transform.CAPITALIZE),
            P(["world"]).expand(Transform.UPPER),
        )
        result = list(pattern.generate())

        # Cartesian product: ["hello", "Hello"] × ["world", "WORLD"]
        expected = ["helloworld", "helloWORLD", "Helloworld", "HelloWORLD"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_por_with_transforms(self):
        """Test POr patterns with transforms."""
        pattern = POr(
            P(["a"]).expand(Transform.UPPER), P(["b"]).expand(Transform.CAPITALIZE)
        )
        result = list(pattern.generate())

        # Should chain: ["a", "A"] + ["b", "B"]
        expected = ["a", "A", "b", "B"]
        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"


class TestRealWorldScenarios:
    """Test more complex, realistic scenarios."""

    def test_base_word_with_suffixes(self):
        """Test common pattern: base word + various endings."""
        pattern = PAnd(
            P(["password"]).expand(Transform.CAPITALIZE, Transform.UPPER),
            P(["", "123", "!"]).expand(),  # No transforms on suffixes
        )

        result = list(pattern.generate())

        # Should have all combinations of transformed base + suffixes
        expected_prefixes = ["password", "Password", "PASSWORD"]
        expected_suffixes = ["", "123", "!"]
        expected = [p + s for p in expected_prefixes for s in expected_suffixes]

        assert sorted(result) == sorted(expected), f"Expected {expected}, got {result}"

    def test_your_original_examples(self):
        """Test the exact examples from your original question."""
        # Test A: P(["test", "testb"]).expand(T.UPPER)
        pattern_a = P(["test", "testb"]).expand(Transform.UPPER)
        result_a = list(pattern_a.generate())
        expected_a = ["test", "TEST", "testb", "TESTB"]
        assert set(result_a) == set(expected_a)

        # Test B: P(["test"]).expand(T.UPPER, T.LOWER)
        pattern_b = P(["test"]).expand(Transform.UPPER, Transform.LOWER)
        result_b = list(pattern_b.generate())
        expected_b = ["test", "TEST"]  # No duplicate "test"
        assert set(result_b) == set(expected_b)

        # Test C: Chained expansion
        pattern_c = P(["a"]).expand(Transform.UPPER).expand(lambda s: s + s)
        result_c = list(pattern_c.generate())
        expected_c = ["a", "A", "aa", "AA"]
        assert set(result_c) == set(expected_c)


if __name__ == "__main__":
    # Run tests directly if called as script
    pytest.main([__file__, "-v"])
