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

    # TOUJOURS en mode headless pour simuler l'environnement GitHub Actions
    chrome_options.add_argument("--headless=new")  # Nouveau mode headless plus stable
    print("[INFO] Mode headless active (simulation GitHub Actions)")

    # Options anti-détection pour contourner les protections SharePoint
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")

    # Masque les indices que c'est un navigateur automatisé
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # User agent pour éviter la détection de bot
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Options spécifiques pour headless
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = None

    try:
        print("[INFO] Demarrage du navigateur Chrome...")

        # Essaie d'utiliser Chrome
        try:
            driver = webdriver.Chrome(options=chrome_options)

            # Masque webdriver avec JavaScript
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })

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

        # Téléchargement via : Fichier → Créer une copie → Télécharger une copie
        print("[INFO] Navigation : Fichier -> Créer une copie -> Télécharger une copie...")

        download_clicked = False

        try:
            # Étape 1 : Cliquer sur "Fichier"
            print("[INFO] Etape 1/3 : Clic sur 'Fichier'...")

            fichier_button = None
            # Sélecteurs pour "Fichier" / "File" (ID stable - priorité absolue)
            selectors_fichier = [
                # Priorité 1 : ID stable (fonctionne en toutes langues)
                (By.ID, "FileMenuFlyoutLauncher"),
                (By.CSS_SELECTOR, "#FileMenuFlyoutLauncher > span"),
                (By.XPATH, "//*[@id='FileMenuFlyoutLauncher']/span"),
                # Priorité 2 : Classes CSS stables
                (By.XPATH, "//button[@id='FileMenuFlyoutLauncher']/span[contains(@class, 'textContainer')]"),
                # Priorité 3 : Fallback par texte (dernière solution)
                (By.XPATH, "//span[text()='File']"),
                (By.XPATH, "//span[text()='Fichier']"),
            ]

            for selector_type, selector_value in selectors_fichier:
                try:
                    print(f"[DEBUG] Tentative Fichier avec: {selector_type} - {str(selector_value)[:60]}")
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

            # Utilise JavaScript pour simuler un vrai clic avec tous les événements
            print("[LOG] Etape: Déclenchement du clic JavaScript sur bouton Fichier")
            print("[LOG] Element trouvé:", fichier_button.get_attribute('id'))

            driver.execute_script("""
                var element = arguments[0];
                console.log('[JS] Element à cliquer:', element);
                var events = ['mousedown', 'mouseup', 'click'];
                events.forEach(function(eventType) {
                    var event = new MouseEvent(eventType, {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    element.dispatchEvent(event);
                    console.log('[JS] Event dispatché:', eventType);
                });
            """, fichier_button)
            print("[LOG] Clic JavaScript exécuté avec succès")

            # Attend que le menu se charge
            print("[LOG] Attente de 3 secondes pour chargement menu...")
            time.sleep(3)
            print("[LOG] Attente terminée")

            # Cherche d'abord DANS l'iframe
            print("[LOG] === Recherche dans IFRAME ===")
            try:
                all_spans_iframe = driver.find_elements(By.TAG_NAME, "span")
                print(f"[LOG] Nombre de spans trouvés dans iframe: {len(all_spans_iframe)}")
                iframe_texts = [s.text.strip() for s in all_spans_iframe[:100] if s.text.strip() and len(s.text.strip()) > 2]
                unique_iframe = list(set(iframe_texts))[:30]
                print(f"[LOG] Textes uniques dans iframe ({len(unique_iframe)}): {unique_iframe}")

                # Cherche spécifiquement "Make" ou "copy"
                make_copy_found = [t for t in iframe_texts if 'make' in t.lower() or 'copy' in t.lower() or 'copie' in t.lower()]
                if make_copy_found:
                    print(f"[LOG] *** TROUVÉ dans iframe: {make_copy_found}")
            except Exception as e:
                print(f"[LOG] Erreur recherche iframe: {e}")

            # Ensuite cherche HORS de l'iframe
            print("[LOG] === Sortie de l'iframe ===")
            driver.switch_to.default_content()
            print("[LOG] Context changé vers page principale")

            print("[LOG] Attente de 2 secondes...")
            time.sleep(2)
            print("[LOG] Attente terminée")

            # Recherche HORS de l'iframe
            print("[LOG] === Recherche dans PAGE PRINCIPALE ===")
            try:
                all_spans_main = driver.find_elements(By.TAG_NAME, "span")
                print(f"[LOG] Nombre de spans trouvés hors iframe: {len(all_spans_main)}")

                main_texts = []
                for span in all_spans_main[:200]:
                    try:
                        text = span.text.strip()
                        if text and len(text) > 2 and len(text) < 50:
                            main_texts.append(text)
                    except:
                        pass

                unique_main = list(set(main_texts))[:40]
                print(f"[LOG] Textes uniques hors iframe ({len(unique_main)}): {unique_main}")

                # Cherche spécifiquement "Make" ou "copy"
                make_copy_main = [t for t in main_texts if 'make' in t.lower() or 'copy' in t.lower() or 'copie' in t.lower()]
                if make_copy_main:
                    print(f"[LOG] *** TROUVÉ hors iframe: {make_copy_main}")
                else:
                    print("[LOG] Aucun texte 'Make', 'copy' ou 'copie' trouvé")
            except Exception as e:
                print(f"[LOG] Erreur recherche main: {e}")

            # Étape 2 : Cliquer sur "Créer une copie" / "Make a copy"
            print("[LOG] === ETAPE 2: Recherche 'Make a copy' ===")
            time.sleep(2 if is_ci else 1)

            copie_button = None
            selectors_copie = [
                (By.XPATH, "//span[contains(text(), 'Make a copy')]"),
                (By.XPATH, "//span[contains(text(), 'Créer une copie')]"),
            ]

            # Augmente le timeout pour CI/CD (menu plus lent à apparaître)
            wait_timeout = 20 if is_ci else 5
            print(f"[LOG] Timeout d'attente: {wait_timeout} secondes")

            for idx, (selector_type, selector_value) in enumerate(selectors_copie, 1):
                print(f"[LOG] Tentative {idx}/{len(selectors_copie)}: {str(selector_value)[:60]}")
                try:
                    # Attend juste la PRÉSENCE (pas clickable), puis on force le clic avec JS
                    print(f"[LOG] Attente de l'élément (max {wait_timeout}s)...")
                    copie_button = WebDriverWait(driver, wait_timeout).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    print(f"[LOG] *** SUCCÈS! Element trouvé avec sélecteur {idx}")
                    print(f"[LOG] Texte de l'élément: {copie_button.text}")
                    break
                except Exception as e:
                    print(f"[LOG] Échec tentative {idx}: {str(e)[:80]}")
                    continue

            if not copie_button:
                print("[LOG] *** ERREUR: Aucun sélecteur n'a fonctionné")
                raise Exception("Impossible de trouver 'Créer une copie'")

            # Utilise JavaScript pour cliquer (plus fiable en headless)
            print("[DEBUG] Clic JavaScript sur 'Créer une copie'")
            driver.execute_script("arguments[0].click();", copie_button)
            time.sleep(3)
            print("[OK] 'Créer une copie' clique")

            # Étape 3 : Cliquer sur "Télécharger une copie"
            print("[INFO] Etape 3/3 : Clic sur 'Télécharger une copie'...")
            time.sleep(2)

            download_button = None
            selectors_download = [
                (By.XPATH, "//span[contains(text(), 'Download a copy')]"),
                (By.XPATH, "//span[contains(text(), 'Télécharger une copie')]"),
            ]

            for selector_type, selector_value in selectors_download:
                try:
                    print(f"[DEBUG] Tentative Télécharger: {str(selector_value)[:60]}")
                    download_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"[OK] 'Télécharger une copie' trouve")
                    break
                except:
                    continue

            if not download_button:
                raise Exception("Impossible de trouver 'Télécharger une copie'")

            # Utilise JavaScript pour cliquer
            print("[DEBUG] Clic JavaScript sur 'Télécharger une copie'")
            driver.execute_script("arguments[0].click();", download_button)
            time.sleep(2)
            print("[OK] Telechargement XLSX lance!")
            download_clicked = True

        except Exception as e:
            print(f"[ERREUR] Impossible de naviguer dans les menus: {e}")
            print("[ERREUR] Le telechargement automatique a echoue")
            return False

        # Si on arrive ici, le téléchargement XLSX a été lancé
        print("[INFO] Attente de la fin du telechargement XLSX...")

        # Vérifie périodiquement si le fichier apparaît
        max_wait = 40  # 40 secondes maximum
        check_interval = 2  # Vérifie toutes les 2 secondes
        elapsed = 0

        # Cherche les fichiers .xlsx dans le dossier de téléchargement
        while elapsed < max_wait:
            time.sleep(check_interval)
            elapsed += check_interval

            # Cherche les fichiers XLSX téléchargés
            xlsx_files = list(Path(download_dir).glob("*.xlsx"))

            # Filtre les fichiers temporaires
            xlsx_files = [f for f in xlsx_files if not f.name.endswith('.crdownload')
                         and not f.name.endswith('.tmp')
                         and not f.name.startswith('~')]

            if xlsx_files:
                # Prend le fichier le plus récent
                latest_file = max(xlsx_files, key=lambda f: f.stat().st_mtime)

                # Vérifie qu'il a été modifié récemment (dans les 40 dernières secondes)
                if time.time() - latest_file.stat().st_mtime < 40:
                    print(f"[OK] Fichier XLSX detecte: {latest_file.name}")

                    # Renomme si nécessaire
                    if str(latest_file) != output_path:
                        import shutil
                        shutil.move(str(latest_file), output_path)
                        print(f"[OK] Fichier renomme vers: {os.path.basename(output_path)}")

                    # Vérifie la taille
                    size_kb = Path(output_path).stat().st_size / 1024
                    print(f"[OK] Taille: {size_kb:.2f} KB")

                    return True

            if elapsed % 10 == 0:
                print(f"  Attente... ({elapsed}/{max_wait}s)")

        print("[ERREUR] Timeout atteint - fichier XLSX non telecharge")
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
