#!/usr/bin/env python3
"""
CRM Automation Main Script
GitHub Actions compatible version
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from extractors.crm_extractor import CRMExtractor
from parsers.svg_parser import extract_highcharts_data
from generators.pptx_generator import PowerPointGenerator


# Slide configuration
SLIDE_CONFIG = [
    {
        'file_pattern': 'jourj_graph2.svg',
        'folder': 'downloads_cf',
        'org': 'ISIM',
        'title': 'Engagement collective quotidienne',
        'button_index': 2,
        'date_type': 'today'
    },
    {
        'file_pattern': 'jourj_graph4.svg',
        'folder': 'downloads_cf',
        'org': 'ISIM',
        'title': 'Productivité individuelle quotidienne',
        'button_index': 4,
        'date_type': 'today'
    },
    {
        'file_pattern': 'semaine_precedente_graph3.svg',
        'folder': 'downloads_cf',
        'org': 'ISIM',
        'title': 'Qualité individuelle quotidienne',
        'button_index': 3,
        'date_type': 'j7'
    },
    {
        'file_pattern': 'semaine_precedente_graph4.svg',
        'folder': 'downloads_cf',
        'org': 'ISIM',
        'title': 'Productivité collectif hebdomadaire',
        'button_index': 4,
        'date_type': 'j7'
    },
    {
        'file_pattern': 'j90_semaine_graph4.svg',
        'folder': 'downloads_cf',
        'org': 'ISIM',
        'title': 'Productivité collectif trimestre',
        'button_index': 4,
        'date_type': 'j90'
    },
    {
        'file_pattern': 'cip_j7_graph0.svg',
        'folder': 'downloads_cip',
        'org': 'Perspectivia',
        'title': 'Productivité collectif hebdomadaire',
        'button_index': 0,
        'date_type': 'j7',
        'stats_type': 'CIP'
    },
    {
        'file_pattern': 'cip_j7_graph2.svg',
        'folder': 'downloads_cip',
        'org': 'Perspectivia',
        'title': 'Engagement collectif hebdomadaire',
        'button_index': 2,
        'date_type': 'j7',
        'stats_type': 'CIP'
    },
    {
        'file_pattern': 'cip_j7_graph4.svg',
        'folder': 'downloads_cip',
        'org': 'ISIM',
        'title': 'Productivité collectif hebdomadaire',
        'button_index': 4,
        'date_type': 'j7',
        'stats_type': 'CIP'
    },
    {
        'file_pattern': 'cip_j90_graph0.svg',
        'folder': 'downloads_cip',
        'org': 'ISIM',
        'title': 'Engagement collective quotidienne',
        'button_index': 0,
        'date_type': 'j90',
        'stats_type': 'CIP'
    },
    {
        'file_pattern': 'cip_jourj_graph0.svg',
        'folder': 'downloads_cip',
        'org': 'Perspectivia',
        'title': 'Productivité collectif quotidienne',
        'button_index': 0,
        'date_type': 'today',
        'stats_type': 'CIP'
    },
    {
        'file_pattern': 'cip_jourj_graph4.svg',
        'folder': 'downloads_cip',
        'org': 'Perspectivia',
        'title': 'Productivité individuelle quotidienne',
        'button_index': 4,
        'date_type': 'today',
        'stats_type': 'CIP'
    }
]


def get_date_range(date_type: str):
    """
    Get date range based on type

    Args:
        date_type: Date type (today, j7, j90)

    Returns:
        tuple: (date_debut, date_fin)
    """
    today = datetime.now()

    if date_type == 'today':
        return today.strftime('%Y-%m-%d'), ''
    elif date_type == 'j7':
        j7 = today - timedelta(days=7)
        return j7.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif date_type == 'j90':
        j90 = today - timedelta(days=92)
        return j90.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    else:
        return today.strftime('%Y-%m-%d'), ''


def extract_data(config_file: str = None):
    """
    Extract data from CRM

    Args:
        config_file: Path to config JSON file
    """
    # Load configuration from environment or file
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Use environment variables
        config = {
            'base_url': os.getenv('CRM_BASE_URL', 'crm.isimcrm.fr'),
            'username': os.getenv('CRM_USERNAME'),
            'password': os.getenv('CRM_PASSWORD'),
            'http_auth_user': os.getenv('CRM_HTTP_AUTH_USER'),
            'http_auth_password': os.getenv('CRM_HTTP_AUTH_PASSWORD')
        }

    # Validate configuration
    if not config['username'] or not config['password']:
        print("❌ ERROR: CRM credentials not configured")
        print("Set CRM_USERNAME and CRM_PASSWORD environment variables")
        sys.exit(1)

    print("="*70)
    print("CRM DATA EXTRACTION")
    print("="*70)

    # Create output directories
    os.makedirs('downloads_cf', exist_ok=True)
    os.makedirs('downloads_cip', exist_ok=True)

    # Initialize extractor
    extractor = CRMExtractor(
        base_url=config['base_url'],
        username=config['username'],
        password=config['password'],
        http_auth_user=config.get('http_auth_user'),
        http_auth_password=config.get('http_auth_password')
    )

    try:
        # Setup driver
        extractor.setup_driver('downloads_cf', headless=True)

        # Login
        extractor.login()

        # Process each slide configuration
        current_stats_type = None
        for i, slide_config in enumerate(SLIDE_CONFIG, 1):
            print(f"\n[{i}/{len(SLIDE_CONFIG)}] Extracting: {slide_config['title']}")

            stats_type = slide_config.get('stats_type', 'CF')

            # Navigate if stats type changed
            if stats_type != current_stats_type:
                extractor.navigate_to_stats(stats_type)
                current_stats_type = stats_type

            # Get date range
            date_debut, date_fin = get_date_range(slide_config['date_type'])

            # Configure form
            extractor.configure_form(
                button_index=slide_config['button_index'],
                date_debut=date_debut,
                date_fin=date_fin
            )

            # Extract SVG
            svg_content = extractor.extract_svg(
                filename=slide_config['file_pattern'],
                button_index=slide_config['button_index']
            )

            if svg_content:
                output_path = os.path.join(slide_config['folder'], slide_config['file_pattern'])
                extractor.save_svg(svg_content, output_path)
            else:
                print(f"⚠️  Failed to extract: {slide_config['file_pattern']}")

        print("\n" + "="*70)
        print("✅ DATA EXTRACTION COMPLETED")
        print("="*70)

    except Exception as e:
        print(f"\n❌ ERROR during extraction: {e}")
        raise

    finally:
        extractor.close()


def generate_report(output_file: str = None):
    """
    Generate PowerPoint report

    Args:
        output_file: Output filename
    """
    print("\n" + "="*70)
    print("POWERPOINT REPORT GENERATION")
    print("="*70)

    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"CRM_Report_{timestamp}.pptx"

    # Initialize generator
    generator = PowerPointGenerator(SLIDE_CONFIG)

    # Create title slide
    generator.create_title_slide(
        title="CRM Report - Specific Data",
        subtitle=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Process each slide
    for i, config in enumerate(SLIDE_CONFIG, 1):
        print(f"\nSlide {i+1}: {config['title']}")

        # Find SVG file
        svg_file = generator.find_svg_file(config['folder'], config['file_pattern'])
        if not svg_file:
            print(f"  [ERROR] SVG file not found: {config['file_pattern']}")
            continue

        print(f"  File found: {os.path.basename(svg_file)}")

        # Parse SVG
        try:
            titre, legendes, valeurs, structure = extract_highcharts_data(svg_file)
            if not structure:
                print(f"  [WARNING] No data extracted")
                continue

        except Exception as e:
            print(f"  [ERROR] Parsing failed: {e}")
            continue

        # Create slide
        generator.create_slide_with_data(
            slide_title=config['title'],
            svg_title=titre,
            data=structure,
            org_filter=config['org'],
            slide_number=i+1
        )

    # Save presentation
    generator.save(output_file)

    return output_file


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='CRM Automation System')
    parser.add_argument('--extract', action='store_true', help='Extract data from CRM')
    parser.add_argument('--generate', action='store_true', help='Generate PowerPoint report')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--output', type=str, help='Output filename')

    args = parser.parse_args()

    # Default: run both extract and generate
    if not args.extract and not args.generate:
        args.extract = True
        args.generate = True

    try:
        if args.extract:
            extract_data(config_file=args.config)

        if args.generate:
            output_file = generate_report(output_file=args.output)
            print(f"\n✅ Report generated: {output_file}")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
