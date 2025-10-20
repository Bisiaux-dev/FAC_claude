#!/usr/bin/env python3
"""
Module d'envoi automatique du rapport avec noms de fichiers sans accents
Version sécurisée pour éviter les problèmes d'encodage
"""

import smtplib
import os
import sys
import zipfile
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
import time
import shutil
import csv
import unicodedata

# Ajouter le dossier parent au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from email_config.email_settings import *
except ImportError:
    print("❌ ERREUR: Configuration email non trouvée")
    sys.exit(1)

def remove_accents(text):
    """Supprime les accents d'une chaîne"""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd if not unicodedata.combining(c))

class CRMReportSender:
    """Gestionnaire d'envoi de rapport CRM"""

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.report_path = os.path.join(self.base_dir, ATTACHMENT_CONFIG['report_filename'])
        self.backup_dir = os.path.join(self.base_dir, ADVANCED_CONFIG['backup_folder'])
        self.checklist_dir = os.path.join(self.base_dir, 'Checklist')

    def get_checklist_stats_from_recap(self):
        """Récupère les statistiques depuis le fichier récapitulatif"""
        recap_file = os.path.join(self.checklist_dir, 'checklist_recap.csv')

        file_mapping = {
            'checklist_équipe_commercial.csv': 'commercial_count',
            'checklist_equipe_commercial.csv': 'commercial_count',
            'checklist_admin_dépôt_initial.csv': 'admin_depot_count',
            'checklist_admin_depot_initial.csv': 'admin_depot_count',
            'checklist_admin_vérifier_dépôt.csv': 'admin_verif_count',
            'checklist_admin_verifier_depot.csv': 'admin_verif_count',
            'checklist_cindy.csv': 'cindy_count',
            'checklist_facturation_en_retard.csv': 'facturation_retard_count',
        }

        stats = {
            'commercial_count': 0,
            'admin_depot_count': 0,
            'admin_verif_count': 0,
            'cindy_count': 0,
            'facturation_retard_count': 0,
        }

        try:
            with open(recap_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader)  # Skip header

                for row in reader:
                    if len(row) >= 2 and row[0] != 'TOTAL':
                        filename = row[0].strip()
                        try:
                            count = int(row[1].strip())
                            count = max(0, count - 1)  # -1 sur chaque comptage
                            if filename in file_mapping:
                                key = file_mapping[filename]
                                stats[key] = max(stats[key], count)
                        except (ValueError, IndexError):
                            continue

            stats['total_count'] = sum(stats.values())

            print(f"STATS: Commercial: {stats['commercial_count']}")
            print(f"STATS: Admin dépôt initial: {stats['admin_depot_count']}")
            print(f"STATS: Admin vérif dépôt: {stats['admin_verif_count']}")
            print(f"STATS: Cindy (facturation): {stats['cindy_count']}")
            print(f"STATS: Facturation en retard: {stats['facturation_retard_count']}")
            print(f"STATS: TOTAL: {stats['total_count']}")

            return stats

        except FileNotFoundError:
            print(f"WARNING: Fichier recap non trouvé")
            return self.get_checklist_stats_fallback()

    def get_checklist_stats_fallback(self):
        """Compte directement les lignes (fallback)"""
        stats = {
            'commercial_count': self.count_checklist_lines('checklist_equipe_commercial.csv'),
            'admin_depot_count': self.count_checklist_lines('checklist_admin_depot_initial.csv'),
            'admin_verif_count': self.count_checklist_lines('checklist_admin_verifier_depot.csv'),
            'cindy_count': self.count_checklist_lines('checklist_cindy.csv'),
            'facturation_retard_count': self.count_checklist_lines('checklist_facturation_en_retard.csv'),
        }
        stats['total_count'] = sum(stats.values())
        return stats

    def count_checklist_lines(self, filename):
        """Compte le nombre de lignes dans un fichier checklist"""
        filepath = os.path.join(self.checklist_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                return max(0, sum(1 for row in reader if any(field.strip() for field in row if field)) - 1)
        except FileNotFoundError:
            return 0
        except Exception:
            return 0

    def get_checklist_stats(self):
        """Récupère les statistiques"""
        return self.get_checklist_stats_from_recap()

    def validate_report_exists(self):
        """Vérifie que le rapport existe"""
        if not ATTACHMENT_CONFIG.get('attach_report', True):
            print("INFO: Envoi sans rapport PowerPoint")
            return True

        if not os.path.exists(self.report_path):
            print("INFO: Rapport PowerPoint non trouvé")
            return True

        return True

    def create_message(self):
        """Crée le message email"""
        msg = MIMEMultipart()

        msg['From'] = formataddr((SENDER_CONFIG['from_name'], SENDER_CONFIG['from_email']))
        msg['To'] = ', '.join(RECIPIENTS_CONFIG['to_emails'])

        if RECIPIENTS_CONFIG['cc_emails']:
            msg['Cc'] = ', '.join(RECIPIENTS_CONFIG['cc_emails'])

        if SENDER_CONFIG['reply_to']:
            msg['Reply-To'] = SENDER_CONFIG['reply_to']

        subject = MESSAGE_CONFIG['subject'].format(
            date=datetime.now().strftime('%Y-%m-%d')
        )
        msg['Subject'] = subject

        generation_date = datetime.now().strftime('%d/%m/%Y à %H:%M')
        stats = self.get_checklist_stats()

        use_html = MESSAGE_CONFIG.get('use_html', False)

        if use_html:
            msg_alternative = MIMEMultipart('alternative')

            body_text = MESSAGE_CONFIG['body_template_text'].format(
                commercial_count=stats['commercial_count'],
                admin_depot_count=stats['admin_depot_count'],
                admin_verif_count=stats['admin_verif_count'],
                cindy_count=stats['cindy_count'],
                facturation_retard_count=stats['facturation_retard_count'],
                total_count=stats['total_count'],
                generation_date=generation_date
            )
            body_text += MESSAGE_CONFIG['signature_text']

            body_html = MESSAGE_CONFIG['body_template_html'].format(
                commercial_count=stats['commercial_count'],
                admin_depot_count=stats['admin_depot_count'],
                admin_verif_count=stats['admin_verif_count'],
                cindy_count=stats['cindy_count'],
                facturation_retard_count=stats['facturation_retard_count'],
                total_count=stats['total_count'],
                generation_date=generation_date
            )
            body_html = body_html.replace('</body>', MESSAGE_CONFIG['signature_html'] + '</body>')

            msg_alternative.attach(MIMEText(body_text, 'plain', 'utf-8'))
            msg_alternative.attach(MIMEText(body_html, 'html', 'utf-8'))

            msg.attach(msg_alternative)
        else:
            body = MESSAGE_CONFIG.get('body_template', MESSAGE_CONFIG['body_template_text']).format(
                commercial_count=stats['commercial_count'],
                admin_depot_count=stats['admin_depot_count'],
                admin_verif_count=stats['admin_verif_count'],
                cindy_count=stats['cindy_count'],
                facturation_retard_count=stats['facturation_retard_count'],
                total_count=stats['total_count'],
                generation_date=generation_date
            )
            body += MESSAGE_CONFIG.get('signature', MESSAGE_CONFIG['signature_text'])
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

        return msg

    def attach_file_safe(self, msg, filepath, safe_filename=None):
        """Attache un fichier avec un nom sans accents"""
        try:
            if not os.path.exists(filepath):
                return False

            original_filename = os.path.basename(filepath)

            if safe_filename is None:
                safe_filename = remove_accents(original_filename)

            if safe_filename.lower().endswith('.csv'):
                maintype = 'text'
                subtype = 'csv'
            elif safe_filename.lower().endswith('.pptx'):
                maintype = 'application'
                subtype = 'vnd.openxmlformats-officedocument.presentationml.presentation'
            else:
                maintype = 'application'
                subtype = 'octet-stream'

            with open(filepath, "rb") as attachment:
                part = MIMEBase(maintype, subtype)
                part.set_payload(attachment.read())

            encoders.encode_base64(part)

            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{safe_filename}"'
            )

            msg.attach(part)
            print(f"  OK: {safe_filename} ({maintype}/{subtype})")
            return True

        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def attach_report(self, msg):
        """Attache le rapport PowerPoint"""
        if not ATTACHMENT_CONFIG.get('attach_report', True):
            return True

        if not os.path.exists(self.report_path):
            return True

        return self.attach_file_safe(msg, self.report_path)

    def attach_checklists(self, msg):
        """Attache les fichiers checklist CSV"""
        if not ATTACHMENT_CONFIG.get('attach_checklists', False):
            return True

        checklist_mapping = {
            'checklist_equipe_commercial.csv': 'checklist_equipe_commercial.csv',
            'checklist_admin_depot_initial.csv': 'checklist_admin_depot_initial.csv',
            'checklist_admin_verifier_depot.csv': 'checklist_admin_verifier_depot.csv',
            'checklist_cindy.csv': 'checklist_cindy.csv',
            'checklist_facturation_en_retard.csv': 'checklist_facturation_en_retard.csv',
            'checklist_recap.csv': 'checklist_recap.csv'
        }

        attached = 0
        for original_name, safe_name in checklist_mapping.items():
            filepath = os.path.join(self.checklist_dir, original_name)
            if self.attach_file_safe(msg, filepath, safe_name):
                attached += 1

        print(f"INFO: {attached}/{len(checklist_mapping)} checklists attachés")
        return True

    def send_email(self, msg):
        """Envoie l'email"""
        for attempt in range(ADVANCED_CONFIG['retry_attempts']):
            try:
                print(f"SENDING: Tentative {attempt + 1}/{ADVANCED_CONFIG['retry_attempts']}...")

                server = smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port'])

                if SMTP_CONFIG['use_tls']:
                    server.starttls()

                server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])

                all_recipients = RECIPIENTS_CONFIG['to_emails'][:]
                if RECIPIENTS_CONFIG['cc_emails']:
                    all_recipients.extend(RECIPIENTS_CONFIG['cc_emails'])
                if RECIPIENTS_CONFIG['bcc_emails']:
                    all_recipients.extend(RECIPIENTS_CONFIG['bcc_emails'])

                server.send_message(msg, to_addrs=all_recipients)
                server.quit()

                print("SUCCESS: Email envoyé avec succès!")
                return True

            except Exception as e:
                print(f"ERROR: {e}")
                if attempt < ADVANCED_CONFIG['retry_attempts'] - 1:
                    time.sleep(ADVANCED_CONFIG['retry_delay_seconds'])

        return False

    def backup_report(self):
        """Sauvegarde le rapport"""
        if not ADVANCED_CONFIG['backup_sent_reports']:
            return

        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)

            if os.path.exists(self.report_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.basename(self.report_path)
                name, ext = os.path.splitext(filename)
                backup_filename = f"{name}_{timestamp}{ext}"
                backup_path = os.path.join(self.backup_dir, backup_filename)

                shutil.copy2(self.report_path, backup_path)
                print(f"BACKUP: Rapport sauvegardé: {backup_filename}")

        except Exception:
            pass

    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        pass

    def send_report(self):
        """Fonction principale"""
        print("=" * 60)
        print("EMAIL PERSPECTIVIA - ENVOI AUTOMATIQUE (VERSION SAFE)")
        print("=" * 60)

        config_errors = validate_config()
        if config_errors:
            print("❌ ERREURS DE CONFIGURATION:")
            for error in config_errors:
                print(f"   • {error}")
            return False

        if not self.validate_report_exists():
            return False

        print("EMAIL: Création du message email...")
        msg = self.create_message()

        if not self.attach_report(msg):
            print("WARNING: Erreur rapport PowerPoint")

        if not self.attach_checklists(msg):
            print("WARNING: Erreur checklists")

        success = self.send_email(msg)

        if success:
            self.backup_report()
            self.cleanup()
            print("SUCCESS: Envoi terminé avec succès!")
            return True
        else:
            print("FAILED: Échec de l'envoi")
            return False

def main():
    """Point d'entrée principal"""
    sender = CRMReportSender()
    success = sender.send_report()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
