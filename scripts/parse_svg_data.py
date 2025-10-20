#!/usr/bin/env python3
"""
Parseur de données SVG pour graphiques Highcharts
Extrait les données des fichiers SVG générés par le CRM
"""

import re
import xml.etree.ElementTree as ET
import os
from typing import Tuple, Dict, List, Any

def extract_highcharts_data(svg_file: str) -> Tuple[str, List[str], Dict[str, Any], Dict[str, Dict[str, float]]]:
    """
    Extrait les données d'un fichier SVG Highcharts
    
    Args:
        svg_file: Chemin vers le fichier SVG
        
    Returns:
        tuple: (titre, legendes, valeurs, structure)
        - titre: Titre du graphique
        - legendes: Liste des noms de séries
        - valeurs: Dict des valeurs par série
        - structure: Dict {centre: {métrique: valeur}}
    """
    
    if not os.path.exists(svg_file):
        print(f"Fichier SVG non trouvé: {svg_file}")
        return "Fichier non trouvé", [], {}, {}
    
    try:
        # Lire le fichier SVG
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Nettoyer les caractères problématiques (zero-width spaces, etc.)
        svg_content = svg_content.replace('\u200b', '')  # Zero-width space
        svg_content = svg_content.replace('\ufeff', '')  # BOM UTF-8
        
        # Parser XML
        root = ET.fromstring(svg_content)
        
        # Définir les namespaces
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # 1. Extraire le titre
        titre = extract_title(root, ns, svg_content)
        
        # 2. Extraire les légendes/séries
        legendes = extract_legends(root, ns)
        
        # 3. Extraire les catégories (axes X)
        categories = extract_categories(root, ns)
        
        # 4. Extraire les valeurs des données
        valeurs_data = extract_data_values(root, ns)
        
        # 5. Construire la structure finale
        structure = build_data_structure(categories, legendes, valeurs_data)
        
        print(f"Données extraites de {os.path.basename(svg_file)}:")
        print(f"  - Titre: {titre}")
        print(f"  - Légendes: {legendes}")
        print(f"  - Catégories: {categories}")
        print(f"  - Structure: {len(structure)} centres trouvés")
        
        return titre, legendes, valeurs_data, structure
        
    except Exception as e:
        print(f"Erreur lors du parsing de {svg_file}: {e}")
        return f"Erreur: {str(e)}", [], {}, {}

def extract_title(root, ns, svg_content: str) -> str:
    """Extrait le titre du graphique"""
    
    # Méthode 1: Via aria-label dans la balise SVG
    svg_element = root
    if 'aria-label' in svg_element.attrib:
        return svg_element.attrib['aria-label']
    
    # Méthode 2: Via balise title class="highcharts-title"
    title_elements = root.findall('.//svg:text[@class="highcharts-title"]', ns)
    if title_elements:
        return title_elements[0].text or "Titre non trouvé"
    
    # Méthode 3: Recherche par regex dans le contenu
    title_match = re.search(r'class="highcharts-title"[^>]*>([^<]+)', svg_content)
    if title_match:
        return title_match.group(1).strip()
    
    # Méthode 4: Via aria-label par regex
    aria_match = re.search(r'aria-label="([^"]+)"', svg_content)
    if aria_match:
        return aria_match.group(1)
    
    return "Titre non trouvé"

def extract_legends(root, ns) -> List[str]:
    """Extrait les légendes/noms des séries"""

    legendes = []

    # Rechercher les éléments de légende avec une approche simplifiée
    for elem in root.iter():
        if elem.get('class') and 'highcharts-legend-item' in elem.get('class'):
            # Chercher le texte dans cet élément
            for text_elem in elem.iter():
                if text_elem.tag.endswith('}text'):
                    # Récupérer TOUT le texte incluant les tspans
                    full_text = ''.join(text_elem.itertext()).strip()
                    if full_text:
                        legendes.append(full_text)
                        break

    return legendes

def extract_categories(root, ns) -> List[str]:
    """Extrait les catégories (axe X)"""

    categories = []

    # Rechercher les labels de l'axe X avec une approche simplifiée
    for elem in root.iter():
        if elem.get('class') and 'highcharts-xaxis-labels' in elem.get('class'):
            # Chercher tous les éléments <text> dans ce groupe
            for text_elem in elem.iter():
                if text_elem.tag.endswith('}text'):
                    # Récupérer TOUT le texte incluant les tspans
                    full_text = ''.join(text_elem.itertext()).strip()
                    if full_text:
                        categories.append(full_text)

    return categories

def extract_data_values(root, ns) -> Dict[str, List[float]]:
    """Extrait les valeurs des données pour chaque série"""

    series_data = {}
    serie_index = 0

    # Rechercher les groupes de data labels par série avec une approche simplifiée
    for elem in root.iter():
        if elem.get('class') and 'highcharts-data-labels' in elem.get('class'):
            series_values = []

            # Trouver tous les labels de données dans ce groupe (INCLUANT LES CACHÉS)
            # Chercher tous les <g class="highcharts-label"> peu importe leur visibilité
            for label_group in elem.iter():
                class_attr = label_group.get('class')
                if class_attr and 'highcharts-label' in class_attr and 'highcharts-data-label' in class_attr:
                    # Extraire le texte, même si opacity="0" ou "highcharts-data-label-hidden"
                    for text_elem in label_group.iter():
                        if text_elem.tag.endswith('}text'):
                            text_content = text_elem.text
                            if text_content and text_content.strip():
                                try:
                                    # Nettoyer TOUS les espaces (normaux, insécables, fines insécables)
                                    value_text = text_content.strip()
                                    value_text = value_text.replace(' ', '')  # Espace normal
                                    value_text = value_text.replace('\xa0', '')  # Espace insécable
                                    value_text = value_text.replace('\u202f', '')  # Espace fine insécable
                                    value_text = value_text.replace('\u2009', '')  # Espace fine
                                    value = float(value_text)
                                    series_values.append(value)
                                    break  # Un seul texte par label
                                except ValueError:
                                    continue

            if series_values:
                series_data[f"Serie_{serie_index}"] = series_values
                serie_index += 1

    return series_data

def build_data_structure(categories: List[str], legendes: List[str], valeurs_data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    """Construit la structure de données finale"""
    
    structure = {}
    
    # S'assurer qu'on a des catégories
    if not categories:
        return structure
    
    # Pour chaque catégorie (centre)
    for i, categorie in enumerate(categories):
        structure[categorie] = {}
        
        # Pour chaque série (métrique)
        serie_index = 0
        for serie_key, valeurs in valeurs_data.items():
            if i < len(valeurs):
                # Utiliser le nom de légende si disponible, sinon le nom de série
                metric_name = legendes[serie_index] if serie_index < len(legendes) else serie_key
                structure[categorie][metric_name] = valeurs[i]
                serie_index += 1
    
    return structure

def test_parser():
    """Fonction de test pour vérifier le parseur"""
    
    # Tester avec les fichiers disponibles
    
    test_files = [
        "../downloads_cf/debug_cf_j90_svg_0.svg",
        "../downloads_cf/debug_cf_j90_svg_1.svg"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n=== Test: {test_file} ===")
            titre, legendes, valeurs, structure = extract_highcharts_data(test_file)
            print(f"Titre: {titre}")
            print(f"Légendes: {legendes}")
            print(f"Structure: {structure}")
        else:
            print(f"Fichier de test non trouvé: {test_file}")

if __name__ == "__main__":
    test_parser()