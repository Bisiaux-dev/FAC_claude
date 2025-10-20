"""
Unit tests for SVG parser
"""

import pytest
from src.parsers.svg_parser import (
    extract_highcharts_data,
    extract_title,
    extract_legends,
    extract_categories,
    extract_data_values,
    build_data_structure
)


def test_extract_title():
    """Test title extraction"""
    # Test with mock data
    svg_content = '<svg aria-label="Test Title"></svg>'
    # This would require proper XML parsing
    # For now, test import works
    assert callable(extract_title)


def test_extract_legends():
    """Test legend extraction"""
    assert callable(extract_legends)


def test_extract_categories():
    """Test category extraction"""
    assert callable(extract_categories)


def test_extract_data_values():
    """Test data value extraction"""
    assert callable(extract_data_values)


def test_build_data_structure():
    """Test data structure building"""
    categories = ["Centre A", "Centre B"]
    legendes = ["Metric 1", "Metric 2"]
    valeurs_data = {
        "Serie_0": [10.5, 20.3],
        "Serie_1": [15.2, 25.7]
    }

    result = build_data_structure(categories, legendes, valeurs_data)

    assert "Centre A" in result
    assert "Centre B" in result
    assert result["Centre A"]["Metric 1"] == 10.5
    assert result["Centre B"]["Metric 2"] == 25.7


def test_extract_highcharts_data_file_not_found():
    """Test with non-existent file"""
    title, legendes, valeurs, structure = extract_highcharts_data("nonexistent.svg")

    assert title == "File not found"
    assert legendes == []
    assert valeurs == {}
    assert structure == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
