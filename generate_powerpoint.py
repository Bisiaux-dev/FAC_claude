#!/usr/bin/env python3
"""
Script pour générer le rapport PowerPoint PERSPECTIVIA
à partir des graphiques générés par t.py
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import glob

# =============================================================================
# CONFIGURATION DYNAMIQUE
# =============================================================================

# Utiliser des chemins relatifs au script
base_directory = os.path.dirname(os.path.abspath(__file__))
graph_directory = os.path.join(base_directory, 'Graphiques')
output_directory = base_directory
output_filename = 'Rapport_PERSPECTIVIA.pptx'

# =============================================================================
# CREATE POWERPOINT PRESENTATION
# =============================================================================

def create_presentation_with_graphs(graph_dir, output_dir, output_file):
    """
    Create a PowerPoint presentation with all graphs from the specified directory
    """
    try:
        # Create a presentation object
        prs = Presentation()
        prs.slide_width = Inches(10)  # Standard 16:9 ratio width
        prs.slide_height = Inches(7.5)  # Standard 16:9 ratio height

        # Add title slide
        title_slide_layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]

        title.text = "Rapport d'Analyse PERSPECTIVIA"
        subtitle.text = "Visualisations des Formations par Vague\nGénéré automatiquement"

        # Get all PNG files from the graph directory
        graph_files = glob.glob(os.path.join(graph_dir, '*.png'))

        if not graph_files:
            print(f"⚠ WARNING: No PNG files found in {graph_dir}")
            return

        # Sort files for consistent ordering
        graph_files.sort()

        print(f"\n📊 Found {len(graph_files)} graphs to add to presentation:")
        for graph_file in graph_files:
            print(f"   - {os.path.basename(graph_file)}")

        # Define graph order and titles
        graph_info = {
            'Paiements_par_Vague.png': 'Paiements Réels par Vague et Type de Paiement',
            'Statut_Formations_par_Vague.png': 'Répartition des Formations par Vague et État',
            'CA_par_Catégorie_Toutes_Vagues.png': 'Chiffre d\'Affaires par Catégorie et par Vague',
            'Statuts_Intermédiaires_Reel.png': 'Statuts Intermédiaires - Réél',
            'Statuts_Intermédiaires_Previsionnel.png': 'Statuts Intermédiaires - Prévisionnel',
            'Statuts_Intermédiaires_Potentiel.png': 'Statuts Intermédiaires - Potentiel',
            'PROMO_Reel_par_Vague.png': 'Répartition des Formations Réelles par PROMO'
        }

        # Add a slide for each graph
        for graph_file in graph_files:
            # Use blank layout for full control
            blank_slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(blank_slide_layout)

            # Get graph filename
            graph_filename = os.path.basename(graph_file)

            # Get title from dictionary or use filename
            slide_title = graph_info.get(graph_filename, graph_filename.replace('.png', '').replace('_', ' '))

            # Add title text box at the top
            left = Inches(0.5)
            top = Inches(0.3)
            width = Inches(9)
            height = Inches(0.6)

            txBox = slide.shapes.add_textbox(left, top, width, height)
            tf = txBox.text_frame
            tf.text = slide_title

            # Format title
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.name = 'Calibri'

            # Add the graph image
            # Calculate dimensions to fit well on slide
            img_left = Inches(0.5)
            img_top = Inches(1.2)
            img_width = Inches(9)

            try:
                pic = slide.shapes.add_picture(graph_file, img_left, img_top, width=img_width)
                print(f"   ✓ Added slide: {slide_title}")
            except Exception as e:
                print(f"   ✗ ERROR adding image {graph_filename}: {e}")

        # Save the presentation
        output_path = os.path.join(output_dir, output_file)
        prs.save(output_path)

        print(f"\n✅ PowerPoint presentation created successfully!")
        print(f"📄 Output file: {output_path}")
        print(f"📊 Total slides: {len(prs.slides)} (1 title + {len(graph_files)} graphs)")

    except Exception as e:
        print(f"❌ ERROR creating PowerPoint presentation: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  POWERPOINT PRESENTATION GENERATOR")
    print("=" * 70)
    print(f"📂 Graph directory: {graph_directory}")
    print(f"📂 Output directory: {output_directory}")

    # Check if graph directory exists
    if not os.path.exists(graph_directory):
        print(f"\n❌ ERROR: Graph directory not found: {graph_directory}")
        print(f"Creating directory: {graph_directory}")
        os.makedirs(graph_directory, exist_ok=True)
    else:
        create_presentation_with_graphs(graph_directory, output_directory, output_filename)

    print("\n" + "=" * 70)
    print("✅ PROCESSING COMPLETE")
    print("=" * 70)
