#!/usr/bin/env python3
"""
Script de lancement interactif pour les 2 workflows d'envoi d'email
"""

import sys
import os

# Définition des workflows
WORKFLOWS = {
    '1': {
        'name': 'WORKFLOW 1: SANS PowerPoint',
        'script': 'email_sender/send_report_without_ppt.py',
        'recipients': [
            'bisiaux.pierre@outlook.fr',
            'C.romeo@planBgroupe.com',
            'b.hunalp@rhreflex.com',
            'aumarin@rhreflex.com',
            'nicolas@perspectivia.fr',
            'markovski@rhreflex.com',
            'stagiaire@isim.fr',
            'zaccharia@isim.fr',
            'perrine@isim.fr',
            'eric@perspectivia.fr',
            'anas@perspectivia.fr',
            'mohamed@perspectivia.fr',
        ],
        'attachments': [
            '8 fichiers Excel (checklists)',
        ],
    },
    '2': {
        'name': 'WORKFLOW 2: AVEC PowerPoint UNIQUEMENT',
        'script': 'email_sender/send_report_with_ppt.py',
        'recipients': [
            'b.hunalp@rhreflex.com',
            'markovski@rhreflex.com',
            'nicolas@perspectivia.fr',
        ],
        'attachments': [
            '1 fichier PowerPoint (Rapport_PERSPECTIVIA.pptx)',
        ],
    }
}

def display_workflow_info(workflow_id):
    """Affiche les informations d'un workflow"""
    workflow = WORKFLOWS[workflow_id]

    print("\n" + "=" * 80)
    print(f"  {workflow['name']}")
    print("=" * 80)

    print(f"\nDESTINATAIRES ({len(workflow['recipients'])} personnes):")
    for i, recipient in enumerate(workflow['recipients'], 1):
        print(f"   {i}. {recipient}")

    print(f"\nPIECES JOINTES:")
    for attachment in workflow['attachments']:
        print(f"   - {attachment}")

    print("\n" + "=" * 80)

def confirm_send():
    """Demande confirmation avant l'envoi"""
    response = input("\n>>> Confirmer l'envoi ? (oui/non): ").strip().lower()
    return response in ['oui', 'o', 'yes', 'y']

def main():
    """Fonction principale"""
    print("\n" + "=" * 80)
    print("  SYSTÈME D'ENVOI EMAIL PERSPECTIVIA")
    print("=" * 80)

    print("\nChoisissez un workflow:")
    print("  1. WORKFLOW 1: Email SANS PowerPoint (12 destinataires)")
    print("  2. WORKFLOW 2: Email AVEC PowerPoint (3 destinataires)")
    print("  0. Annuler")

    choice = input("\nVotre choix (1/2/0): ").strip()

    if choice == '0':
        print("\n❌ Annulé par l'utilisateur")
        sys.exit(0)

    if choice not in ['1', '2']:
        print("\n❌ Choix invalide")
        sys.exit(1)

    # Afficher les informations du workflow
    display_workflow_info(choice)

    # Demander confirmation
    if not confirm_send():
        print("\n❌ Envoi annulé par l'utilisateur")
        sys.exit(0)

    # Lancer le script d'envoi
    workflow = WORKFLOWS[choice]
    script_path = os.path.join(os.path.dirname(__file__), workflow['script'])

    print("\n>>> Lancement de l'envoi...")
    print("=" * 80 + "\n")

    # Exécuter le script
    os.system(f'python "{script_path}"')

if __name__ == "__main__":
    main()
