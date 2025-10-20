#!/usr/bin/env python3
"""
Module d'envoi d'email pour le rapport PowerPoint CRM
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from email_config import EMAIL_CONFIG

def send_powerpoint_email(pptx_path, duration, tests_success, ppt_success):
    """
    Envoie le fichier PowerPoint par email

    Args:
        pptx_path (str): Chemin vers le fichier PowerPoint
        duration (float): Durée d'exécution en secondes
        tests_success (bool): Succès des tests Robot
        ppt_success (bool): Succès de la génération PowerPoint

    Returns:
        bool: True si l'envoi a réussi, False sinon
    """

    # Vérifier si l'email est activé
    if not EMAIL_CONFIG.get('email_enabled', True):
        print("Envoi d'email desactive dans la configuration")
        print("Changez 'email_enabled': True dans email_config.py pour activer")
        return False

    try:
        # Vérifier que le fichier existe
        if not os.path.exists(pptx_path):
            print(f"ERREUR: Fichier PowerPoint non trouvé: {pptx_path}")
            return False

        # Informations sur le fichier
        file_size = os.path.getsize(pptx_path) / 1024  # Taille en KB
        filename = os.path.basename(pptx_path)

        # Informations de date/heure
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")

        # Status en français
        tests_status = "Succès" if tests_success else "Échec"
        ppt_status = "Succès" if ppt_success else "Échec"

        print(f"\n{'='*50}")
        print(">> ENVOI DU RAPPORT PAR EMAIL")
        print(f"{'='*50}")
        print(f"Fichier: {filename}")
        print(f"Taille: {file_size:.1f} KB")
        print(f"Destinataires: {', '.join(EMAIL_CONFIG['recipients'])}")

        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = ', '.join(EMAIL_CONFIG['recipients'])
        msg['Subject'] = EMAIL_CONFIG['subject'].format(date=date_str)

        # Corps du message
        body = EMAIL_CONFIG['body_template'].format(
            date=date_str,
            time=time_str,
            duration=f"{duration:.1f}",
            tests_status=tests_status,
            ppt_status=ppt_status,
            file_size=f"{file_size:.1f}"
        )

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Ajouter la pièce jointe
        print("Attachement du fichier PowerPoint...")
        with open(pptx_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        msg.attach(part)

        # Connexion SMTP et envoi
        print("Connexion au serveur SMTP...")
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.ehlo()  # Identification auprès du serveur
        server.starttls()  # Activer la sécurité
        server.ehlo()  # Re-identification après TLS

        print("Authentification...")
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])

        print("Envoi en cours...")
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipients'], text)
        server.quit()

        print("EMAIL ENVOYE AVEC SUCCES!")
        print(f"   Destinataires: {len(EMAIL_CONFIG['recipients'])} personne(s)")
        print(f"   Taille du fichier envoye: {file_size:.1f} KB")

        return True

    except smtplib.SMTPAuthenticationError:
        print("ERREUR: Echec de l'authentification SMTP")
        print("   Verifiez vos identifiants dans email_config.py")
        print("   Pour Outlook, activez l'authentification 2 facteurs")
        print("   et utilisez un mot de passe d'application")
        return False

    except smtplib.SMTPConnectError:
        print("ERREUR: Impossible de se connecter au serveur SMTP")
        print(f"   Serveur: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
        return False

    except Exception as e:
        print(f"ERREUR lors de l'envoi d'email: {e}")
        return False

def test_email_config():
    """
    Test la configuration email sans envoyer de fichier
    """
    print("Test de la configuration email...")

    try:
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.quit()

        print("Configuration email valide!")
        return True

    except Exception as e:
        print(f"Configuration email invalide: {e}")
        return False

if __name__ == "__main__":
    import sys

    # Si un argument est fourni, envoyer le rapport
    if len(sys.argv) > 1:
        pptx_path = sys.argv[1]
        print(f"Envoi du rapport: {pptx_path}")

        # Paramètres par défaut pour l'envoi
        duration = 0  # Non disponible depuis la ligne de commande
        tests_success = True  # Supposer succès si le fichier existe
        ppt_success = True  # Supposer succès si le fichier existe

        success = send_powerpoint_email(pptx_path, duration, tests_success, ppt_success)
        sys.exit(0 if success else 1)
    else:
        # Test de la configuration
        print("Mode test - Aucun fichier spécifié")
        test_email_config()