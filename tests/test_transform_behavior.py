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
    """Test the core transform behavior of patterns."""

    def test_single_transform_includes_original(self):
        """Test that single transform includes original + transformed."""
        pattern = P(["test"]).alter(Transform.UPPER)
        result = list(pattern.generate())
        
        expected = ["test", "TEST"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_multiple_items_with_transform(self):
        """Test multiple items each get original + transformed."""
        pattern = P(["hello", "world"]).alter(Transform.CAPITALIZE)
        result = list(pattern.generate())
        
        expected = ["hello", "Hello", "world", "World"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_multiple_transforms_no_duplicates(self):
        """Test multiple transforms avoid duplicates but include original."""
        pattern = P(["Test"]).alter(Transform.UPPER, Transform.CAPITALIZE)
        result = list(pattern.generate())
        
        # Original "Test", UPPER "TEST", CAPITALIZE "Test" (duplicate of original)
        expected = ["Test", "TEST"]  # No duplicate "Test"
        assert result == expected, f"Expected {expected}, got {result}"

    def test_lambda_transform_includes_original(self):
        """Test lambda transforms include original."""
        pattern = P(["hello"]).alter(lambda x: x + "!")
        result = list(pattern.generate())
        
        expected = ["hello", "hello!"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_mixed_transform_types(self):
        """Test mixing Transform enum and lambda functions."""
        pattern = P(["test"]).alter(Transform.UPPER, lambda x: x + "123")
        result = list(pattern.generate())
        
        expected = ["test", "TEST", "test123"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_no_transforms_returns_original(self):
        """Test pattern with no transforms returns original items."""
        pattern = P(["original", "items"])
        result = list(pattern.generate())
        
        expected = ["original", "items"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_empty_alter_returns_original(self):
        """Test calling .alter() with no arguments returns original."""
        pattern = P(["test"]).alter()
        result = list(pattern.generate())
        
        expected = ["test"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_chained_alters(self):
        """Test chaining multiple .alter() calls."""
        pattern = P(["hello"]).alter(Transform.UPPER).alter(lambda x: x + "!")
        result = list(pattern.generate())
        
        # Chained alters work like method chaining: each .alter() operates on 
        # the results of the previous pattern, not just the original items
        expected = ["hello", "hello!", "HELLO", "HELLO!"]
        assert set(result) == set(expected), f"Expected {set(expected)}, got {set(result)}"

    def test_leet_transform_includes_original(self):
        """Test leet transformations include original."""
        pattern = P(["password"]).alter(Transform.LEET_BASIC)
        result = list(pattern.generate())
        
        expected = ["password", "p@$$w0rd"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_numeric_transforms(self):
        """Test numeric zero-padding transforms."""
        pattern = P(["5", "42"]).alter(Transform.ZERO_PAD_2)
        result = list(pattern.generate())
        
        # "42" zero-padded to 2 digits is still "42", so duplicate is removed
        expected = ["5", "05", "42"]  # No duplicate "42"
        assert result == expected, f"Expected {expected}, got {result}"

    def test_case_sensitive_duplicates_avoided(self):
        """Test that case transforms avoid creating duplicates."""
        pattern = P(["HELLO"]).alter(Transform.UPPER, Transform.LOWER)
        result = list(pattern.generate())
        
        expected = ["HELLO", "hello"]  # UPPER of "HELLO" is duplicate
        assert result == expected, f"Expected {expected}, got {result}"


class TestEstimateCount:
    """Test that estimate_count reflects the new behavior."""

    def test_estimate_with_no_transforms(self):
        """Test count estimation with no transforms."""
        pattern = P(["a", "b", "c"])
        assert pattern.estimate_count() == 3  # Just original items

    def test_estimate_with_single_transform(self):
        """Test count estimation with single transform."""
        pattern = P(["a", "b"]).alter(Transform.UPPER)
        # 2 items * (1 original + 1 transform) = 4
        assert pattern.estimate_count() == 4

    def test_estimate_with_multiple_transforms(self):
        """Test count estimation with multiple transforms."""
        pattern = P(["test"]).alter(Transform.UPPER, Transform.LOWER)
        # 1 item * (1 original + 2 transforms) = 3
        assert pattern.estimate_count() == 3

    def test_estimate_with_lambda_transforms(self):
        """Test count estimation includes lambda transforms."""
        pattern = P(["hello"]).alter(lambda x: x + "!", lambda x: x[::-1])
        # 1 item * (1 original + 2 lambda transforms) = 3
        assert pattern.estimate_count() == 3


class TestCompositePatterns:
    """Test that composite patterns work correctly with new behavior."""

    def test_pand_with_transforms(self):
        """Test PAnd patterns with transforms."""
        pattern = PAnd(
            P(["hello"]).alter(Transform.CAPITALIZE),
            P(["world"]).alter(Transform.UPPER)
        )
        result = list(pattern.generate())
        
        # Cartesian product: ["hello", "Hello"] × ["world", "WORLD"]
        expected = ["helloworld", "helloWORLD", "Helloworld", "HelloWORLD"]
        assert result == expected, f"Expected {expected}, got {result}"

    def test_por_with_transforms(self):
        """Test POr patterns with transforms."""
        pattern = POr(
            P(["a"]).alter(Transform.UPPER),
            P(["b"]).alter(Transform.CAPITALIZE)
        )
        result = list(pattern.generate())
        
        # Should chain: ["a", "A"] + ["b", "B"]
        expected = ["a", "A", "b", "B"]
        assert result == expected, f"Expected {expected}, got {result}"


class TestRealWorldScenarios:
    """Test realistic password generation scenarios."""

    def test_base_word_with_suffixes(self):
        """Test common pattern: base word + various endings."""
        pattern = PAnd(
            P(["password"]).alter(Transform.CAPITALIZE, Transform.UPPER),
            P(["", "123", "!"]).alter()  # No transforms on suffixes
        )
        
        result = list(pattern.generate())
        
        # Should have all combinations of transformed base + suffixes
        expected_prefixes = ["password", "Password", "PASSWORD"]
        expected_suffixes = ["", "123", "!"]
        expected = [p + s for p in expected_prefixes for s in expected_suffixes]
        
        assert result == expected, f"Expected {expected}, got {result}"

    def test_your_original_examples(self):
        """Test the exact examples from your original question."""
        # Test A: P(["test", "testb"]).alter(T.UPPER)
        pattern_a = P(["test", "testb"]).alter(Transform.UPPER)
        result_a = list(pattern_a.generate())
        expected_a = ['test', 'TEST', 'testb', 'TESTB']
        assert set(result_a) == set(expected_a)

        # Test B: P(["test", "testb"]).alter(T.UPPER, lambda x: x)  
        pattern_b = P(["test", "testb"]).alter(Transform.UPPER, lambda x: x)
        result_b = list(pattern_b.generate())
        expected_b = ['test', 'TEST', 'testb', 'TESTB']  # lambda x: x creates duplicates but they're filtered
        assert set(result_b) == set(expected_b)

        # Test C: P(["test", "testb"]).alter()
        pattern_c = P(["test", "testb"]).alter()
        result_c = list(pattern_c.generate())
        expected_c = ['test', 'testb']
        assert result_c == expected_c


if __name__ == "__main__":
    # Run tests directly if called as script
    pytest.main([__file__, "-v"]) 