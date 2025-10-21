#!/usr/bin/env python3
"""
Configuration des paramètres d'envoi d'email pour le rapport PERSPECTIVIA
"""

import os

# Configuration SMTP
SMTP_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    # Utiliser les variables d'environnement (GitHub Actions)
    'username': os.getenv('SMTP_USERNAME', 'bisiauxpierre2@gmail.com'),
    'password': os.getenv('SMTP_PASSWORD', 'owlg osev vszn fuyp'),
}

# Configuration expéditeur
SENDER_CONFIG = {
    'from_email': 'bisiauxpierre2@gmail.com',
    'from_name': 'CRM Automation System',
    'reply_to': 'bisiauxpierre2@gmail.com',
}

# Configuration des destinataires
RECIPIENTS_CONFIG = {
    'to_emails': [
        'bisiaux.pierre@outlook.fr',
        'C.romeo@planBgroupe.com',
        'b.hunalp@rhreflex.com',
        # 'aumarin@rhreflex.com',
        # 'nicolas@perspectivia.fr',
        # 'markovski@rhreflex.com',
        # 'stagiaire@isim.fr',
        # 'zaccharia@isim.fr',
        # 'perrine@isim.fr',
        # 'eric@perspectivia.fr',
        # 'anas@perspectivia.fr',
        # 'mohamed@perspectivia.fr',
    ],
    'cc_emails': [],
    'bcc_emails': [],
}

# Configuration du message
MESSAGE_CONFIG = {
    'subject': 'Rapport PERSPECTIVIA - Checklists par équipe ({date})',
    'body_template_text': '''
Bonjour,

Voici le nombre de checklists identifiés par équipe :

COMMERCIAL
({commercial_count}) nombre de ligne dans checklist_équipe_commercial
=> {commercial_count} dossiers doivent être relancés par l'équipe commercial afin de récupérer les signatures manquantes

ADMINISTRATIF
({admin_depot_count}) nombre de ligne dans checklist_admin_dépôt_initial
=> {admin_depot_count} dossiers doivent être déposés en brouillon par l'équipe administrative

({admin_verif_count}) nombre de ligne dans checklist_admin_vérifier_dépôt
=> {admin_verif_count} dossiers doivent être déposés par l'équipe administrative auprès de la plateforme de l'OPCO

COMPTABILITÉ
({cindy_count}) nombre de ligne dans checklist_cindy
=> {cindy_count} dossiers doivent être facturés par la comptabilité

({facturation_retard_count}) nombre de ligne dans checklist_facturation_en_retard
=> {facturation_retard_count} dossiers doivent être facturés par la comptabilité pour l'échéance 2

TOTAL : {total_count} dossiers à traiter

Date de génération : {generation_date}

Cordialement,
Système d'automatisation PERSPECTIVIA
''',
    'body_template_html': '''
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;">
    <p>Bonjour,</p>

    <p>Voici le nombre de checklists identifiés par équipe :</p>

    <p><strong style="font-size: 16px;">COMMERCIAL</strong><br>
    ({commercial_count}) nombre de ligne dans checklist_équipe_commercial<br>
    =&gt; {commercial_count} dossiers doivent être relancés par l'équipe commercial afin de récupérer les signatures manquantes</p>

    <p><strong style="font-size: 16px;">ADMINISTRATIF</strong><br>
    ({admin_depot_count}) nombre de ligne dans checklist_admin_dépôt_initial<br>
    =&gt; {admin_depot_count} dossiers doivent être déposés en brouillon par l'équipe administrative</p>

    <p>({admin_verif_count}) nombre de ligne dans checklist_admin_vérifier_dépôt<br>
    =&gt; {admin_verif_count} dossiers doivent être déposés par l'équipe administrative auprès de la plateforme de l'OPCO</p>

    <p><strong style="font-size: 16px;">COMPTABILITÉ</strong><br>
    ({cindy_count}) nombre de ligne dans checklist_cindy<br>
    =&gt; {cindy_count} dossiers doivent être facturés par la comptabilité</p>

    <p>({facturation_retard_count}) nombre de ligne dans checklist_facturation_en_retard<br>
    =&gt; {facturation_retard_count} dossiers doivent être facturés par la comptabilité pour l'échéance 2</p>

    <p><strong>TOTAL : {total_count} dossiers à traiter</strong></p>

    <p>Date de génération : {generation_date}</p>

    <p>Cordialement,<br>
    Système d'automatisation PERSPECTIVIA</p>
</body>
</html>
''',
    'signature_text': '''
---
Ce rapport a été généré automatiquement par FAC Automation
Pour toute question technique, contactez bisiaux.pierre@outlook.fr
''',
    'signature_html': '''
<hr style="border: 1px solid #ccc; margin: 20px 0;">
<p style="font-size: 12px; color: #666;">
Ce rapport a été généré automatiquement par FAC Automation<br>
Pour toute question technique, contactez <a href="mailto:bisiaux.pierre@outlook.fr">bisiaux.pierre@outlook.fr</a>
</p>
''',
    'use_html': True,
}

# Configuration des pièces jointes
ATTACHMENT_CONFIG = {
    'report_filename': 'Rapport_PERSPECTIVIA.pptx',
    'max_size_mb': 25,
    'compress_if_needed': True,
    'attach_report': False,  # PowerPoint désactivé
    'attach_checklists': True,  # Joindre les CSV
    'additional_files': [],
}

# Configuration avancée
ADVANCED_CONFIG = {
    'retry_attempts': 3,
    'retry_delay_seconds': 30,
    'send_on_success_only': True,
    'include_logs_on_error': True,
    'delete_after_send': False,
    'backup_sent_reports': True,
    'backup_folder': 'sent_reports',
}

def validate_config():
    """Valide la configuration d'email"""
    errors = []

    if not SMTP_CONFIG['username']:
        errors.append("SMTP username non configuré")

    if not SMTP_CONFIG['password']:
        errors.append("SMTP password non configuré")

    if not SENDER_CONFIG['from_email']:
        errors.append("Email expéditeur non configuré")

    if not RECIPIENTS_CONFIG['to_emails']:
        errors.append("Aucun destinataire configuré")

    return errors

def load_from_env():
    """Charge la configuration depuis les variables d'environnement"""
    if os.getenv('SMTP_USERNAME'):
        SMTP_CONFIG['username'] = os.getenv('SMTP_USERNAME')

    if os.getenv('SMTP_PASSWORD'):
        SMTP_CONFIG['password'] = os.getenv('SMTP_PASSWORD')

    if os.getenv('FROM_EMAIL'):
        SENDER_CONFIG['from_email'] = os.getenv('FROM_EMAIL')

    if os.getenv('TO_EMAILS'):
        RECIPIENTS_CONFIG['to_emails'] = os.getenv('TO_EMAILS').split(',')

load_from_env()
