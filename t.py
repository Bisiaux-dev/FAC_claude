#!/usr/bin/env python3
"""
Script simplifié pour générer les checklists
ATTENTION: Ce script nécessite le fichier Excel source
"""

import os
import sys

def main():
    print("=" * 60)
    print("GÉNÉRATION DES CHECKLISTS - FAC PERSPECTIVIA")
    print("=" * 60)
    print()

    # Vérifier si le fichier Excel existe
    excel_file = "NOUVEAU FAC PERSPECTIVIA (3) (1).xlsx"

    if not os.path.exists(excel_file):
        print(f"⚠️  ATTENTION: Le fichier Excel '{excel_file}' n'est pas présent")
        print()
        print("Pour que ce script fonctionne, vous devez :")
        print("1. Ajouter le fichier Excel source dans ce dossier")
        print("2. Ou modifier ce script pour pointer vers le bon fichier")
        print()
        print("En attendant, le script utilisera les checklists existants si disponibles.")
        print()

        # Vérifier si les checklists existent déjà
        checklist_dir = "Checklist"
        if os.path.exists(checklist_dir) and os.path.isdir(checklist_dir):
            csv_files = [f for f in os.listdir(checklist_dir) if f.endswith('.csv')]
            if csv_files:
                print(f"✅ {len(csv_files)} fichiers checklist trouvés dans {checklist_dir}/")
                for f in csv_files:
                    print(f"   - {f}")
                print()
                print("Les checklists existants seront utilisés pour l'envoi d'email.")
                return 0
            else:
                print(f"❌ Aucun fichier checklist trouvé dans {checklist_dir}/")
                return 1
        else:
            print(f"❌ Le dossier {checklist_dir}/ n'existe pas")
            return 1

    print(f"✅ Fichier Excel trouvé: {excel_file}")
    print()
    print("TODO: Implémenter le traitement du fichier Excel")
    print("(Le code complet de traitement sera ajouté ici)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
