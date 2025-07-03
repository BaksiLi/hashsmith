#!/usr/bin/env python3
"""
Comprehensive test cases for HashSmith pattern engine.

Tests all pattern types and their interactions.
"""

import sys
from pathlib import Path
import pytest

# Setup path to import from src
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from hashsmith.patterns.engine import P, PAnd, POr, Birthday, Transform, save_to_file


class TestBirthdayPatterns:
    """Test Birthday pattern generation."""

    def test_birthday_basic_mmdd(self):
        """Test basic MMDD birthday format."""
        pattern = Birthday(years=[1990], formats=["MMDD"])
        result = list(pattern.generate())
        
        # Should have 12 months * 31 days (minus invalid dates)
        # January 1990: 0101, 0102, ..., 0131
        assert "0101" in result  # Jan 1st
        assert "0131" in result  # Jan 31st
        assert "1225" in result  # Dec 25th
        
        # Should not have impossible dates (though our current implementation might include some)
        # The Birthday pattern has a rough date validation
        assert "0431" not in result  # April 31st - this should be filtered out

    def test_birthday_handles_leap_and_non_leap_years(self):
        """Test that Feb 29 is generated for leap years but not for non-leap years."""
        # 1992 is a leap year
        leap_pattern = Birthday(years=[1992], formats=["MMDD"])
        leap_results = list(leap_pattern.generate())
        assert "0229" in leap_results, "Feb 29th should exist in a leap year"

        # 1991 is not a leap year
        non_leap_pattern = Birthday(years=[1991], formats=["MMDD"])
        non_leap_results = list(non_leap_pattern.generate())
        assert "0229" not in non_leap_results, "Feb 29th should not exist in a non-leap year"

        # General date validation
        assert "0431" not in non_leap_results, "April 31st should never exist"

    def test_birthday_multiple_formats(self):
        """Test multiple birthday formats."""
        pattern = Birthday(years=[1990], formats=["MMDD", "YYMMDD"])
        result = list(pattern.generate())
        
        # Should have both formats
        assert "0101" in result      # MMDD format
        assert "900101" in result    # YYMMDD format
        
        # Estimate should reflect multiple formats
        assert pattern.estimate_count() > 365  # More than just MMDD

    def test_birthday_multiple_years(self):
        """Test multiple birth years."""
        pattern = Birthday(years=[1990, 1991], formats=["YYMMDD"])
        result = list(pattern.generate())
        
        # Should have both years
        assert "900101" in result    # 1990
        assert "910101" in result    # 1991


class TestLengthConstraints:
    """Test pattern generation with length constraints."""

    def test_length_filtering(self):
        """Test min/max length filtering."""
        pattern = PAnd(
            P(["a", "bb"]),
            P(["1", "22", "333"])
        )
        
        # No constraints - should get all combinations
        all_results = list(pattern.generate())
        expected_all = ["a1", "a22", "a333", "bb1", "bb22", "bb333"]
        assert all_results == expected_all
        
        # Min length 3 - should filter out short ones
        min_3_results = list(pattern.generate(min_len=3))
        expected_min_3 = ["a22", "a333", "bb1", "bb22", "bb333"]
        assert min_3_results == expected_min_3
        
        # Max length 3 - should filter out long ones
        max_3_results = list(pattern.generate(max_len=3))
        expected_max_3 = ["a1", "a22", "bb1"]
        assert max_3_results == expected_max_3
        
        # Range 3-4 - should filter both ends
        range_results = list(pattern.generate(min_len=3, max_len=4))
        expected_range = ["a22", "a333", "bb1", "bb22"]  # "a333" is length 4, so included
        assert range_results == expected_range


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_pattern_list(self):
        """Test pattern with empty list."""
        pattern = P([])
        result = list(pattern.generate())
        assert result == []
        assert pattern.estimate_count() == 0

    def test_empty_string_in_pattern(self):
        """Test pattern containing empty string."""
        pattern = P(["", "test"])
        result = list(pattern.generate())
        expected = ["", "test"]
        assert result == expected

    def test_duplicate_items_in_pattern(self):
        """Test pattern with duplicate items."""
        pattern = P(["test", "test", "hello"])
        result = list(pattern.generate())
        expected = ["test", "test", "hello"]  # Duplicates preserved
        assert result == expected

    def test_very_long_string(self):
        """Test pattern with very long strings."""
        long_string = "a" * 1000
        pattern = P([long_string])
        result = list(pattern.generate(max_len=2000))  # Set higher max length
        assert result == [long_string]

    def test_unicode_strings(self):
        """Test pattern with unicode characters."""
        pattern = P(["café", "naïve", "résumé"]).alter(Transform.UPPER)
        result = list(pattern.generate())
        
        # Should handle unicode properly
        assert "café" in result
        assert "CAFÉ" in result
        assert "naïve" in result


class TestTransformEdgeCases:
    """Test edge cases in transform behavior."""

    def test_leet_speak_comprehensive(self):
        """Test comprehensive leet speak transformations."""
        pattern = P(["password"]).alter(Transform.LEET_BASIC)
        result = list(pattern.generate())
        
        assert "password" in result
        assert "p@$$w0rd" in result

    def test_zero_padding_non_numeric(self):
        """Test zero padding on non-numeric strings."""
        pattern = P(["abc", "123"]).alter(Transform.ZERO_PAD_4)
        result = list(pattern.generate())
        
        # abc unchanged by zero padding, 123 becomes 0123, but duplicates are removed
        expected = ["abc", "123", "0123"]  # No duplicate "abc"
        assert result == expected

    def test_reverse_transform(self):
        """Test reverse transformation."""
        pattern = P(["hello", "world"]).alter(Transform.REVERSE)
        result = list(pattern.generate())
        
        expected = ["hello", "olleh", "world", "dlrow"]
        assert result == expected

    def test_title_case_transform(self):
        """Test title case transformation."""
        pattern = P(["hello world", "test case"]).alter(Transform.TITLE)
        result = list(pattern.generate())
        
        expected = ["hello world", "Hello World", "test case", "Test Case"]
        assert result == expected


class TestComplexCompositions:
    """Test complex pattern compositions."""

    def test_nested_compositions(self):
        """Test deeply nested pattern compositions."""
        inner_or = POr(P(["a"]), P(["b"]))
        middle_and = PAnd(P(["x"]), inner_or, P(["z"]))
        outer_or = POr(middle_and, P(["simple"]))
        
        result = list(outer_or.generate())
        expected = ["xaz", "xbz", "simple"]
        assert result == expected

    def test_realistic_password_pattern(self):
        """Test a realistic password generation pattern."""
        pattern = PAnd(
            # Base words with capitalization
            P(["admin", "user", "pass"]).alter(Transform.CAPITALIZE),
            
            # Optional separator
            POr(P([""]), P(["-", "_"])),
            
            # Numbers or years
            POr(
                P(["123", "456"]),
                Birthday(years=[2020, 2021], formats=["YYYY"])
            ),
            
            # Optional suffix
            POr(P([""]), P(["!", "$"]))
        )
        
        result = list(pattern.generate())
        
        # Should contain various realistic combinations
        assert "admin123" in result
        # Note: with new chaining behavior, results include both original and capitalized
        # Let's check for patterns that should definitely be there
        assert any("admin" in pwd and "123" in pwd for pwd in result)
        assert any("Admin" in pwd and "2020" in pwd for pwd in result)
        assert any("user" in pwd or "User" in pwd for pwd in result)


class TestFileOperations:
    """Test file save operations."""

    def test_save_to_file(self, tmp_path):
        """Test saving patterns to file."""
        pattern = P(["test1", "test2"]).alter(Transform.UPPER)
        output_file = tmp_path / "test_output.txt"
        
        count = save_to_file(pattern, output_file, min_len=1, max_len=10)
        
        # Should save 4 items: test1, TEST1, test2, TEST2
        assert count == 4
        assert output_file.exists()
        
        # Read and verify content
        content = output_file.read_text().strip().split('\n')
        expected = ["test1", "TEST1", "test2", "TEST2"]
        assert content == expected

    def test_save_with_max_count_limit(self, tmp_path):
        """Test saving with max count limit."""
        pattern = P(["a", "b", "c", "d", "e"])
        output_file = tmp_path / "limited_output.txt"
        
        count = save_to_file(pattern, output_file, min_len=1, max_len=10, max_count=3)
        
        # Should save only 3 items due to limit
        assert count == 3
        
        content = output_file.read_text().strip().split('\n')
        assert len(content) == 3
        assert content == ["a", "b", "c"]


class TestPerformance:
    """Test performance considerations."""

    def test_large_pattern_estimation(self):
        """Test estimation for large patterns."""
        # Create a pattern that would generate many combinations
        pattern = PAnd(
            P(["a", "b", "c"]).alter(Transform.UPPER, Transform.LOWER),
            P(["1", "2", "3"]),
            P(["x", "y"])
        )
        
        # Each P generates: 3 items * (1 + 2 transforms) = 9 for first pattern
        # Total: 9 * 3 * 2 = 54 combinations
        estimated = pattern.estimate_count()
        actual = len(list(pattern.generate()))
        
        # Estimation might not be exact due to deduplication, but should be reasonable
        assert estimated >= actual  # Estimate should be >= actual
        assert estimated <= actual * 2  # But not wildly off


if __name__ == "__main__":
    # Run tests directly if called as script
    pytest.main([__file__, "-v"]) 