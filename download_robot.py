#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robot de téléchargement automatique depuis SharePoint
Utilise Selenium pour automatiser le navigateur
Adapté pour le projet FAC PERSPECTIVIA
"""

import os
import sys
import time
from pathlib import Path

def install_selenium():
    """Installe Selenium si nécessaire"""
    try:
        import selenium
        print("[OK] Selenium est deja installe")
        return True
    except ImportError:
        print("[INFO] Installation de Selenium...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "selenium"],
                              capture_output=True)
        if result.returncode == 0:
            print("[OK] Selenium installe avec succes")
            return True
        else:
            print("[ERREUR] Impossible d'installer Selenium")
            return False

def download_sharepoint_file(username, password, url, output_path):
    """
    Télécharge un fichier depuis SharePoint en automatisant le navigateur

    Args:
        username: Email de connexion
        password: Mot de passe
        url: URL du fichier SharePoint
        output_path: Chemin où sauvegarder le fichier
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

    print("\n" + "="*70)
    print("  ROBOT DE TELECHARGEMENT SHAREPOINT - FAC PERSPECTIVIA")
    print("="*70)
    print()

    # Configuration du navigateur Chrome
    chrome_options = Options()

    # Configuration du dossier de téléchargement
    download_dir = os.path.abspath(os.path.dirname(output_path))
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Détecte si on est dans un environnement CI/CD (GitHub Actions, etc.)
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

    if is_ci:
        # Mode headless obligatoire pour CI/CD
        chrome_options.add_argument("--headless=new")  # Nouveau mode headless plus stable
        print("[INFO] Mode CI/CD detecte - Mode headless active")
    else:
        # Mode graphique pour usage local (debugging plus facile)
        print("[INFO] Mode local - Mode graphique active")

    # Options communes pour tous les environnements
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")

    # User agent pour éviter la détection de bot
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Options spécifiques pour CI/CD
    if is_ci:
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--remote-debugging-port=9222")
    else:
        chrome_options.add_argument("--start-maximized")

    driver = None

    try:
        print("[INFO] Demarrage du navigateur Chrome...")

        # Essaie d'utiliser Chrome
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("[OK] Chrome demarre")
        except Exception as e:
            print(f"[WARN] Impossible de demarrer Chrome: {e}")
            print("[INFO] Tentative avec Edge...")

            # Essaie avec Edge
            try:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                from selenium.webdriver.edge.service import Service as EdgeService

                edge_options = EdgeOptions()
                edge_options.add_experimental_option("prefs", prefs)

                driver = webdriver.Edge(options=edge_options)
                print("[OK] Edge demarre")
            except Exception as e2:
                print(f"[ERREUR] Impossible de demarrer Edge: {e2}")
                print()
                print("SOLUTION:")
                print("  1. Verifiez que Chrome ou Edge est installe")
                print("  2. Ou installez ChromeDriver:")
                print("     https://chromedriver.chromium.org/")
                return False

        print(f"[INFO] Acces a SharePoint: {url}")
        driver.get(url)

        # Attend la page de connexion Microsoft
        print("[INFO] Attente de la page de connexion...")
        time.sleep(3)

        # Détecte si on est sur une page de connexion
        try:
            # Recherche le champ email
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "loginfmt"))
            )
            print("[OK] Page de connexion detectee")

            # Entre l'email
            print(f"[INFO] Saisie de l'email: {username}")
            email_field.clear()
            email_field.send_keys(username)

            # Clique sur "Suivant"
            next_button = driver.find_element(By.ID, "idSIButton9")
            next_button.click()
            time.sleep(3)

            # Entre le mot de passe
            print("[INFO] Saisie du mot de passe...")
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "passwd"))
            )
            password_field.clear()
            password_field.send_keys(password)

            # Clique sur "Se connecter"
            signin_button = driver.find_element(By.ID, "idSIButton9")
            signin_button.click()
            time.sleep(3)

            # Gère la question "Rester connecté"
            try:
                stay_signed_in = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "idSIButton9"))
                )
                print("[INFO] Clic sur 'Oui' (Rester connecte)")
                stay_signed_in.click()
                time.sleep(3)
            except TimeoutException:
                print("[INFO] Pas de question 'Rester connecte'")

            print("[OK] Connexion reussie!")

        except TimeoutException:
            print("[INFO] Pas de page de connexion detectee (deja connecte?)")

        # Attend que la page SharePoint soit chargée
        print("[INFO] Attente du chargement de SharePoint...")
        time.sleep(8)

        # Affiche l'URL actuelle pour debug
        print(f"[DEBUG] URL actuelle: {driver.current_url}")
        print(f"[DEBUG] Titre de la page: {driver.title}")

        # Bascule vers l'iframe Excel Online
        print("[INFO] Recherche de l'iframe Excel Online...")
        time.sleep(5)

        try:
            # Cherche l'iframe WacFrame_Excel
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"[DEBUG] {len(iframes)} iframe(s) trouve(s)")

            for iframe in iframes:
                iframe_id = iframe.get_attribute("id")
                if "WacFrame" in str(iframe_id) or "Excel" in str(iframe_id):
                    print(f"[OK] Iframe Excel trouve: {iframe_id}")
                    driver.switch_to.frame(iframe)
                    print("[OK] Bascule vers l'iframe reussie")
                    break
            else:
                # Si aucun iframe spécifique trouvé, essaie le premier
                if iframes:
                    print("[INFO] Bascule vers le premier iframe...")
                    driver.switch_to.frame(0)

            time.sleep(3)
        except Exception as e:
            print(f"[WARN] Impossible de basculer vers iframe: {e}")
            print("[INFO] Continuation sans iframe...")

        # Téléchargement via : Fichier → Exporter → Télécharger au format CSV
        print("[INFO] Navigation dans les menus : Fichier -> Exporter -> CSV...")

        download_clicked = False

        try:
            # Étape 1 : Cliquer sur "Fichier"
            print("[INFO] Etape 1/3 : Clic sur 'Fichier'...")

            fichier_button = None
            # Essaie plusieurs méthodes pour trouver le bouton "Fichier"
            selectors = [
                (By.ID, "FileMenuFlyoutLauncher"),
                (By.CSS_SELECTOR, "#FileMenuFlyoutLauncher > span"),
                (By.XPATH, "//*[@id='FileMenuFlyoutLauncher']/span"),
                (By.XPATH, "//span[contains(@class, 'textContainer') and contains(text(), 'Fichier')]"),
                (By.XPATH, "//button[@id='FileMenuFlyoutLauncher']//span"),
            ]

            for selector_type, selector_value in selectors:
                try:
                    print(f"[DEBUG] Tentative avec: {selector_type} - {selector_value}")
                    fichier_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"[OK] Bouton 'Fichier' trouve avec: {selector_type}")
                    break
                except Exception as e:
                    print(f"[DEBUG] Echec: {str(e)[:50]}")
                    continue

            if not fichier_button:
                raise Exception("Impossible de trouver le bouton 'Fichier'")

            fichier_button.click()
            time.sleep(3)
            print("[OK] Menu 'Fichier' ouvert")

            # Capture d'écran pour debug (si en mode CI/CD)
            if is_ci:
                try:
                    screenshot_path = os.path.join(download_dir, "debug_menu_fichier.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"[DEBUG] Screenshot sauvegarde: {screenshot_path}")
                except:
                    pass

            # Étape 2 : Cliquer sur "Exporter"
            print("[INFO] Etape 2/3 : Clic sur 'Exporter'...")
            time.sleep(3)

            exporter_button = None
            # Essaie plusieurs méthodes pour trouver "Exporter"
            selectors_exporter = [
                (By.XPATH, "//span[contains(text(), 'Exporter')]"),
                (By.XPATH, "//span[contains(text(), 'Export')]"),  # Version anglaise
                (By.XPATH, "//*[contains(@class, 'MenuItem') and contains(., 'Exporter')]"),
                (By.XPATH, "//*[contains(@class, 'MenuItem') and contains(., 'Export')]"),
                (By.XPATH, "//button[contains(., 'Exporter')]"),
                (By.XPATH, "//button[contains(., 'Export')]"),
                (By.XPATH, "//*[@role='menuitem' and contains(., 'Exporter')]"),
                (By.XPATH, "//*[@role='menuitem' and contains(., 'Export')]"),
            ]

            for selector_type, selector_value in selectors_exporter:
                try:
                    print(f"[DEBUG] Tentative Exporter avec: {selector_type} - {selector_value[:50]}")
                    exporter_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"[OK] Bouton 'Exporter' trouve avec: {selector_type}")
                    break
                except Exception as e:
                    print(f"[DEBUG] Echec: {str(e)[:50]}")
                    continue

            if not exporter_button:
                raise Exception("Impossible de trouver le bouton 'Exporter'")

            exporter_button.click()
            time.sleep(2)
            print("[OK] Menu 'Exporter' ouvert")

            # Étape 3 : Cliquer sur "Télécharger au format CSV" (ou "Download as CSV")
            print("[INFO] Etape 3/3 : Clic sur 'Telecharger au format CSV'...")
            time.sleep(2)

            csv_button = None
            # Essaie plusieurs méthodes pour trouver "Télécharger au format CSV" / "Download as CSV"
            selectors_csv = [
                # Versions françaises
                (By.XPATH, "//span[text()='Télécharger au format CSV']"),
                (By.XPATH, "//span[contains(text(), 'Télécharger au format CSV') and not(contains(text(), 'UTF'))]"),
                (By.XPATH, "//*[contains(@class, 'MenuItem')]//span[contains(text(), 'Télécharger au format CSV')]"),
                (By.XPATH, "//*[@role='menuitem' and contains(., 'Télécharger au format CSV')]"),
                # Versions anglaises
                (By.XPATH, "//span[text()='Download as CSV']"),
                (By.XPATH, "//span[contains(text(), 'Download') and contains(text(), 'CSV') and not(contains(text(), 'UTF'))]"),
                (By.XPATH, "//*[contains(@class, 'MenuItem')]//span[contains(text(), 'Download') and contains(text(), 'CSV')]"),
                (By.XPATH, "//*[@role='menuitem' and contains(., 'Download') and contains(., 'CSV')]"),
            ]

            for selector_type, selector_value in selectors_csv:
                try:
                    print(f"[DEBUG] Tentative CSV avec: {selector_type} - {selector_value[:60]}")
                    csv_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"[OK] Bouton 'CSV' trouve avec: {selector_type}")
                    break
                except Exception as e:
                    print(f"[DEBUG] Echec: {str(e)[:50]}")
                    continue

            if not csv_button:
                raise Exception("Impossible de trouver le bouton 'Télécharger au format CSV / Download as CSV'")

            csv_button.click()
            time.sleep(2)
            print("[OK] Telechargement CSV lance!")
            download_clicked = True

        except Exception as e:
            print(f"[ERREUR] Impossible de naviguer dans les menus: {e}")
            print("[ERREUR] Le telechargement automatique a echoue")
            return False

        # Si on arrive ici, le clic sur CSV a réussi
        # Attend que le téléchargement soit terminé
        print("[INFO] Attente de la fin du telechargement...")

        # Vérifie périodiquement si le fichier apparaît
        max_wait = 30  # 30 secondes maximum
        check_interval = 2  # Vérifie toutes les 2 secondes
        elapsed = 0

        # Cherche les fichiers .csv ou .xlsx dans le dossier de téléchargement
        while elapsed < max_wait:
            time.sleep(check_interval)
            elapsed += check_interval

            # Cherche les fichiers téléchargés (CSV ou XLSX)
            csv_files = list(Path(download_dir).glob("*.csv"))
            xlsx_files = list(Path(download_dir).glob("*.xlsx"))
            all_files = csv_files + xlsx_files

            # Filtre les fichiers temporaires
            all_files = [f for f in all_files if not f.name.endswith('.crdownload')
                         and not f.name.endswith('.tmp')
                         and not f.name.startswith('~')]

            if all_files:
                # Prend le fichier le plus récent
                latest_file = max(all_files, key=lambda f: f.stat().st_mtime)

                # Vérifie qu'il a été modifié récemment (dans les 30 dernières secondes)
                if time.time() - latest_file.stat().st_mtime < 30:
                    print(f"[OK] Fichier detecte: {latest_file.name}")

                    # Le fichier de sortie doit toujours être .xlsx pour FAC
                    final_path = output_path

                    # Si c'est un CSV, on le convertit en Excel
                    if latest_file.suffix == '.csv':
                        print("[INFO] Conversion CSV -> Excel...")
                        try:
                            import pandas as pd
                            df = pd.read_csv(str(latest_file), sep=';', encoding='utf-8-sig')
                            df.to_excel(final_path, index=False, engine='openpyxl')
                            print(f"[OK] Fichier converti et sauvegarde: {os.path.basename(final_path)}")
                            # Supprime le CSV temporaire
                            latest_file.unlink()
                        except Exception as e:
                            print(f"[WARN] Erreur conversion CSV: {e}")
                            print("[INFO] Conservation du fichier CSV original")
                            # Renomme en .xlsx même si c'est du CSV (t.py pourra le lire)
                            import shutil
                            shutil.move(str(latest_file), final_path)
                    else:
                        # C'est déjà un XLSX, renomme si nécessaire
                        if str(latest_file) != final_path:
                            import shutil
                            shutil.move(str(latest_file), final_path)
                            print(f"[OK] Fichier renomme vers: {os.path.basename(final_path)}")

                    # Vérifie la taille
                    size_kb = Path(final_path).stat().st_size / 1024
                    print(f"[OK] Taille: {size_kb:.2f} KB")

                    return True

            if elapsed % 10 == 0:
                print(f"  Attente... ({elapsed}/{max_wait}s)")

        print("[ERREUR] Timeout atteint - fichier non telecharge")
        return False

    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if driver:
            print()
            print("[INFO] Fermeture du navigateur dans 5 secondes...")
            print("        (Appuyez sur Ctrl+C pour garder la fenetre ouverte)")
            try:
                time.sleep(5)
                driver.quit()
                print("[OK] Navigateur ferme")
            except KeyboardInterrupt:
                print("[INFO] Navigateur laisse ouvert")
            except:
                pass

def main():
    """Fonction principale"""
    print()
    print("="*70)
    print("  ROBOT DE TELECHARGEMENT SHAREPOINT")
    print("  Automatisation avec Selenium")
    print("  FAC PERSPECTIVIA")
    print("="*70)
    print()

    # Vérifie et installe Selenium
    if not install_selenium():
        return 1

    # Configuration depuis les variables d'environnement
    username = os.getenv('SHAREPOINT_USERNAME', 'b.hunalp@rhreflex.com')
    password = os.getenv('SHAREPOINT_PASSWORD', '')  # Optionnel !
    sharepoint_url = os.getenv('SHAREPOINT_URL',
        'https://cfanice-my.sharepoint.com/:x:/g/personal/b_hunalp_rhreflex_com/EU3ys-Z0yutBt2ZsX2OtAIABRVINihppyXSB6hoDyH6WBw?e=gUu1iE')

    # Chemin de sortie
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "NOUVEAU FAC PERSPECTIVIA.xlsx")

    # Les credentials sont optionnels si c'est un lien de partage public
    if password:
        print(f"[INFO] Mode: Authentification avec credentials")
        print(f"[INFO] Username: {username}")
    else:
        print(f"[INFO] Mode: Lien de partage public (sans authentification)")
        print(f"[INFO] Les credentials SharePoint ne sont pas requis")

    print(f"[INFO] URL: {sharepoint_url}")
    print(f"[INFO] Output: {output_path}")
    print()

    # Lance le téléchargement
    success = download_sharepoint_file(username, password, sharepoint_url, output_path)

    if success:
        print()
        print("="*70)
        print("  SUCCES - TELECHARGEMENT TERMINE!")
        print("="*70)
        print()
        print(f"Fichier: {output_path}")
        print()
        print("Vous pouvez maintenant lancer le traitement avec:")
        print("  python t.py")
        print()
        return 0
    else:
        print()
        print("="*70)
        print("  ECHEC DU TELECHARGEMENT")
        print("="*70)
        print()
        print("Solutions:")
        print("  1. Verifiez les identifiants")
        print("  2. Verifiez que le lien SharePoint est valide")
        print("  3. Telechargez manuellement le fichier")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
