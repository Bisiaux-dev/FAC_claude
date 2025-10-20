#!/usr/bin/env python3
"""
SVG Parser for Highcharts Data Extraction
Extracts data from CRM-generated SVG files
"""

import re
import xml.etree.ElementTree as ET
import os
from typing import Tuple, Dict, List, Any


def extract_highcharts_data(svg_file: str) -> Tuple[str, List[str], Dict[str, Any], Dict[str, Dict[str, float]]]:
    """
    Extract data from Highcharts SVG file

    Args:
        svg_file: Path to SVG file

    Returns:
        tuple: (title, legends, values, structure)
    """

    if not os.path.exists(svg_file):
        print(f"SVG file not found: {svg_file}")
        return "File not found", [], {}, {}

    try:
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        root = ET.fromstring(svg_content)
        ns = {'svg': 'http://www.w3.org/2000/svg'}

        # Extract title
        titre = extract_title(root, ns, svg_content)

        # Extract legends/series
        legendes = extract_legends(root, ns)

        # Extract categories (X-axis)
        categories = extract_categories(root, ns)

        # Extract data values
        valeurs_data = extract_data_values(root, ns)

        # Build final structure
        structure = build_data_structure(categories, legendes, valeurs_data)

        print(f"Data extracted from {os.path.basename(svg_file)}:")
        print(f"  - Title: {titre}")
        print(f"  - Legends: {legendes}")
        print(f"  - Categories: {categories}")
        print(f"  - Structure: {len(structure)} centers found")

        return titre, legendes, valeurs_data, structure

    except Exception as e:
        print(f"Error parsing {svg_file}: {e}")
        return f"Error: {str(e)}", [], {}, {}


def extract_title(root, ns, svg_content: str) -> str:
    """Extract chart title using multiple methods"""

    # Method 1: Via aria-label in SVG tag
    svg_element = root
    if 'aria-label' in svg_element.attrib:
        return svg_element.attrib['aria-label']

    # Method 2: Via title tag with class="highcharts-title"
    title_elements = root.findall('.//svg:text[@class="highcharts-title"]', ns)
    if title_elements:
        return title_elements[0].text or "Title not found"

    # Method 3: Regex search in content
    title_match = re.search(r'class="highcharts-title"[^>]*>([^<]+)', svg_content)
    if title_match:
        return title_match.group(1).strip()

    # Method 4: Via aria-label with regex
    aria_match = re.search(r'aria-label="([^"]+)"', svg_content)
    if aria_match:
        return aria_match.group(1)

    return "Title not found"


def extract_legends(root, ns) -> List[str]:
    """Extract legend/series names"""

    legendes = []

    for elem in root.iter():
        if elem.get('class') and 'highcharts-legend-item' in elem.get('class'):
            for text_elem in elem.iter():
                if text_elem.tag.endswith('}text') and text_elem.text and text_elem.text.strip():
                    legendes.append(text_elem.text.strip())
                    break

    return legendes


def extract_categories(root, ns) -> List[str]:
    """Extract categories (X-axis)"""

    categories = []

    for elem in root.iter():
        if elem.get('class') and 'highcharts-xaxis-labels' in elem.get('class'):
            for text_elem in elem.iter():
                if text_elem.tag.endswith('}text') and text_elem.text and text_elem.text.strip():
                    categories.append(text_elem.text.strip())

    return categories


def extract_data_values(root, ns) -> Dict[str, List[float]]:
    """Extract data values for each series"""

    series_data = {}
    serie_index = 0

    for elem in root.iter():
        if elem.get('class') and 'highcharts-data-labels' in elem.get('class'):
            series_values = []

            for label_group in elem.iter():
                class_attr = label_group.get('class')
                if class_attr and 'highcharts-label' in class_attr and 'highcharts-data-label' in class_attr:
                    for text_elem in label_group.iter():
                        if text_elem.tag.endswith('}text'):
                            text_content = text_elem.text
                            if text_content and text_content.strip():
                                try:
                                    # Clean all types of spaces
                                    value_text = text_content.strip()
                                    value_text = value_text.replace(' ', '')  # Normal space
                                    value_text = value_text.replace('\xa0', '')  # Non-breaking space
                                    value_text = value_text.replace('\u202f', '')  # Narrow no-break space
                                    value_text = value_text.replace('\u2009', '')  # Thin space
                                    value = float(value_text)
                                    series_values.append(value)
                                    break
                                except ValueError:
                                    continue

            if series_values:
                series_data[f"Serie_{serie_index}"] = series_values
                serie_index += 1

    return series_data


def build_data_structure(categories: List[str], legendes: List[str], valeurs_data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    """Build final data structure"""

    structure = {}

    if not categories:
        return structure

    for i, categorie in enumerate(categories):
        structure[categorie] = {}

        serie_index = 0
        for serie_key, valeurs in valeurs_data.items():
            if i < len(valeurs):
                metric_name = legendes[serie_index] if serie_index < len(legendes) else serie_key
                structure[categorie][metric_name] = valeurs[i]
                serie_index += 1

    return structure


if __name__ == "__main__":
    print("SVG Parser module loaded successfully")
