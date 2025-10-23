#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robot de téléchargement automatique depuis SharePoint
Version simplifiée - Télécharge le XLSX sans modification
"""

import os
import sys
import time
from pathlib import Path

def download_sharepoint_file(url, output_path):
    """Télécharge un fichier depuis SharePoint"""
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options

    print("="*70)
    print("  TÉLÉCHARGEMENT SHAREPOINT - FAC PERSPECTIVIA")
    print("="*70)

    # Configuration Chrome
    chrome_options = Options()
    download_dir = os.path.abspath(os.path.dirname(output_path))

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Mode headless si CI/CD
    if os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true':
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

    driver = None

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[INFO] Accès à SharePoint...")
        driver.get(url)
        time.sleep(5)

        # Basculer vers iframe Excel
        print("[INFO] Recherche de l'iframe Excel...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            iframe_id = iframe.get_attribute("id")
            if "WacFrame" in str(iframe_id) or "Excel" in str(iframe_id):
                driver.switch_to.frame(iframe)
                print(f"[OK] Iframe trouvé: {iframe_id}")
                break
        time.sleep(3)

        # Clic sur "Fichier"
        print("[INFO] Clic sur 'Fichier'...")
        fichier_selectors = [
            (By.ID, "FileMenuFlyoutLauncher"),
            (By.CSS_SELECTOR, "#FileMenuFlyoutLauncher > span"),
        ]

        for selector_type, selector_value in fichier_selectors:
            try:
                fichier_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                fichier_button.click()
                break
            except:
                continue
        time.sleep(3)

        # Clic sur "Créer une copie"
        print("[INFO] Clic sur 'Créer une copie'...")
        copie_selectors = [
            (By.XPATH, "//span[contains(text(), 'Créer une copie')]"),
            (By.XPATH, "//span[contains(text(), 'Make a copy')]"),
        ]

        for selector_type, selector_value in copie_selectors:
            try:
                copie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                copie_button.click()
                break
            except:
                continue
        time.sleep(3)

        # Clic sur "Télécharger une copie"
        print("[INFO] Clic sur 'Télécharger une copie'...")
        download_selectors = [
            (By.XPATH, "//span[contains(text(), 'Télécharger une copie')]"),
            (By.XPATH, "//span[contains(text(), 'Download a copy')]"),
        ]

        for selector_type, selector_value in download_selectors:
            try:
                download_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                download_button.click()
                print("[OK] Téléchargement lancé!")
                time.sleep(5)  # Attendre 5s pour que le téléchargement démarre
                break
            except:
                continue

        # Attente du fichier
        print("[INFO] Attente du fichier...")
        max_wait = 90  # Augmenté à 90 secondes pour GitHub Actions
        elapsed = 0

        while elapsed < max_wait:
            time.sleep(2)
            elapsed += 2

            # Debug: lister tous les fichiers
            all_files = list(Path(download_dir).glob("*"))
            if elapsed % 10 == 0:  # Log toutes les 10 secondes
                print(f"[DEBUG] {elapsed}s - Fichiers présents: {len(all_files)}")

            xlsx_files = list(Path(download_dir).glob("*.xlsx"))
            xlsx_files = [f for f in xlsx_files if not f.name.endswith('.crdownload')
                         and not f.name.startswith('~')]

            if xlsx_files:
                latest_file = max(xlsx_files, key=lambda f: f.stat().st_mtime)
                if time.time() - latest_file.stat().st_mtime < 30:
                    print(f"[OK] Fichier détecté: {latest_file.name}")

                    # Renommer si nécessaire
                    if str(latest_file) != output_path:
                        import shutil
                        shutil.move(str(latest_file), output_path)
                        print(f"[OK] Fichier renommé vers: {os.path.basename(output_path)}")

                    size_kb = Path(output_path).stat().st_size / 1024
                    print(f"[OK] Taille: {size_kb:.2f} KB")
                    return True

        print("[ERREUR] Timeout - fichier non téléchargé")
        return False

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if driver:
            time.sleep(2)
            driver.quit()
            print("[OK] Navigateur fermé")


def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("  ROBOT DE TÉLÉCHARGEMENT SHAREPOINT")
    print("="*70)

    # Configuration
    sharepoint_url = os.getenv('SHAREPOINT_URL',
        'https://cfanice-my.sharepoint.com/:x:/g/personal/b_hunalp_rhreflex_com/EU3ys-Z0yutBt2ZsX2OtAIABRVINihppyXSB6hoDyH6WBw?e=gUu1iE')

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "NOUVEAU FAC PERSPECTIVIA.xlsx")

    print(f"[INFO] URL: {sharepoint_url}")
    print(f"[INFO] Output: {output_path}\n")

    # Téléchargement
    success = download_sharepoint_file(sharepoint_url, output_path)

    if success:
        print("\n" + "="*70)
        print("  SUCCÈS - TÉLÉCHARGEMENT TERMINÉ!")
        print("="*70)
        print(f"\nFichier: {output_path}")
        print("\nVous pouvez maintenant lancer le traitement avec:")
        print("  python pt2.py\n")
        return 0
    else:
        print("\n" + "="*70)
        print("  ÉCHEC DU TÉLÉCHARGEMENT")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
