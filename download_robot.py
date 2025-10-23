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

    # Mode headless si CI/CD
    if os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true':
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Options pour éviter la détection headless et permettre le téléchargement
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')

        # Préférences supplémentaires pour forcer le téléchargement
        prefs["profile.default_content_setting_values.automatic_downloads"] = 1

    # Appliquer les préférences Chrome (une seule fois)
    chrome_options.add_experimental_option("prefs", prefs)

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
            # Sélecteurs par ID et CSS
            (By.ID, "FileMenuFlyoutLauncher"),
            (By.CSS_SELECTOR, "#FileMenuFlyoutLauncher > span"),
            # Sélecteurs XPath
            (By.XPATH, "//*[@id='FileMenuFlyoutLauncher']/span"),
            (By.XPATH, "/html/body/div[4]/form/div[2]/div[1]/div[1]/div[3]/div/div[3]/div/div/div[1]/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[1]/div/div/button/span"),
            # Sélecteurs par texte (FR + EN)
            (By.XPATH, "//span[contains(@class, 'textContainer') and contains(text(), 'Fichier')]"),
            (By.XPATH, "//span[contains(@class, 'textContainer') and contains(text(), 'File')]"),
            (By.XPATH, "//button[contains(., 'Fichier')]//span"),
            (By.XPATH, "//button[contains(., 'File')]//span"),
        ]

        fichier_clicked = False
        for selector_type, selector_value in fichier_selectors:
            try:
                print(f"[DEBUG] Essai sélecteur Fichier: {selector_value}")
                fichier_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                fichier_button.click()
                print("[OK] Bouton 'Fichier' cliqué!")
                fichier_clicked = True
                break
            except Exception as e:
                continue

        if not fichier_clicked:
            print("[ERREUR] Impossible de cliquer sur 'Fichier'")

        time.sleep(3)

        # Clic sur "Créer une copie"
        print("[INFO] Clic sur 'Créer une copie'...")
        copie_selectors = [
            # Sélecteurs CSS spécifiques
            (By.CSS_SELECTOR, "#menur67 > span.fui-MenuItem__content"),
            (By.CSS_SELECTOR, "#menur67 > span.fui-MenuItem__content.r1ls86vo"),
            # Sélecteurs XPath spécifiques
            (By.XPATH, "//*[@id='menur67']/span[2]"),
            (By.XPATH, "/html/body/div[23]/div/div/div/div/div[3]/div[2]/span[2]"),
            # Sélecteurs par texte (FR + EN)
            (By.XPATH, "//span[contains(@class, 'fui-MenuItem__content') and contains(text(), 'Créer une copie')]"),
            (By.XPATH, "//span[contains(@class, 'fui-MenuItem__content') and contains(text(), 'Make a copy')]"),
            (By.XPATH, "//span[contains(text(), 'Créer une copie')]"),
            (By.XPATH, "//span[contains(text(), 'Make a copy')]"),
            (By.XPATH, "//div[contains(., 'Créer une copie')]//span"),
            (By.XPATH, "//div[contains(., 'Make a copy')]//span"),
        ]

        copie_clicked = False
        for selector_type, selector_value in copie_selectors:
            try:
                print(f"[DEBUG] Essai sélecteur Créer une copie: {selector_value}")
                copie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                copie_button.click()
                print("[OK] Bouton 'Créer une copie' cliqué!")
                copie_clicked = True
                break
            except Exception as e:
                continue

        if not copie_clicked:
            print("[ERREUR] Impossible de cliquer sur 'Créer une copie'")

        time.sleep(3)

        # Clic sur "Télécharger une copie"
        print("[INFO] Clic sur 'Télécharger une copie'...")
        download_selectors = [
            # Sélecteurs par texte EXACT (FR + EN) - Les plus fiables
            (By.XPATH, "//span[contains(@class, 'fui-MenuItem__content') and text()='Télécharger une copie']"),
            (By.XPATH, "//span[contains(@class, 'fui-MenuItem__content') and text()='Download a copy']"),
            (By.XPATH, "//span[text()='Télécharger une copie']"),
            (By.XPATH, "//span[text()='Download a copy']"),
            # Sélecteurs par texte CONTAINS (FR + EN)
            (By.XPATH, "//span[contains(@class, 'fui-MenuItem__content') and contains(text(), 'Télécharger une copie')]"),
            (By.XPATH, "//span[contains(@class, 'fui-MenuItem__content') and contains(text(), 'Download a copy')]"),
            (By.XPATH, "//span[contains(text(), 'Télécharger une copie')]"),
            (By.XPATH, "//span[contains(text(), 'Download a copy')]"),
            # Sélecteurs XPath spécifiques (en dernier recours)
            (By.XPATH, "//*[@id='MainApp']/div[24]/div/div/div/div/div/div[2]/span[2]"),
            (By.XPATH, "/html/body/div[24]/div/div/div/div/div/div[2]/span[2]"),
            # Sélecteurs CSS (éviter le trop générique)
            (By.CSS_SELECTOR, "#MainApp > div:nth-child(53) > div > div > div > div > div > div:nth-child(2) > span.fui-MenuItem__content"),
        ]

        download_clicked = False
        for selector_type, selector_value in download_selectors:
            try:
                print(f"[DEBUG] Essai sélecteur Télécharger une copie: {selector_value}")
                download_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                download_button.click()
                print("[OK] Bouton 'Télécharger une copie' cliqué!")
                download_clicked = True

                # Screenshot pour debug en CI/CD
                if os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true':
                    try:
                        driver.save_screenshot('/tmp/sharepoint_download.png')
                        print("[DEBUG] Screenshot sauvegardé: /tmp/sharepoint_download.png")
                    except:
                        pass

                time.sleep(5)  # Attendre 5s pour que le téléchargement démarre
                break
            except Exception as e:
                continue

        if not download_clicked:
            print("[ERREUR] Impossible de cliquer sur 'Télécharger une copie'")

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
