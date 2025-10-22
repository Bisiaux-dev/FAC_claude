# 📧 Workflows d'Envoi Email PERSPECTIVIA

Ce projet contient 2 workflows d'automatisation distincts pour l'envoi quotidien des rapports PERSPECTIVIA.

## 🔄 Les 2 Workflows

### **Workflow 1 : Email SANS PowerPoint**
- **Fichier** : `.github/workflows/workflow1_sans_powerpoint.yml`
- **Déclenchement** : Tous les jours à 8h00 (Paris) ou manuellement
- **Destinataires** : 12 personnes (toute l'équipe)
  1. bisiaux.pierre@outlook.fr
  2. C.romeo@planBgroupe.com
  3. b.hunalp@rhreflex.com
  4. aumarin@rhreflex.com
  5. nicolas@perspectivia.fr
  6. markovski@rhreflex.com
  7. stagiaire@isim.fr
  8. zaccharia@isim.fr
  9. perrine@isim.fr
  10. eric@perspectivia.fr
  11. anas@perspectivia.fr
  12. mohamed@perspectivia.fr

- **Pièces jointes** : 8 fichiers Excel
  - checklist_equipe_commercial.xlsx
  - depot_que_le_client_doit_effectuer.xlsx
  - checklist_admin_depot_initial.xlsx
  - checklist_admin_verifier_depot.xlsx
  - checklist_cindy.xlsx
  - checklist_facturation_en_retard.xlsx
  - tresorerie_en_retard.xlsx
  - checklist_recap.xlsx

---

### **Workflow 2 : Email AVEC PowerPoint**
- **Fichier** : `.github/workflows/workflow2_avec_powerpoint.yml`
- **Déclenchement** : Tous les jours à 8h00 (Paris) ou manuellement
- **Destinataires** : 3 personnes (management)
  1. b.hunalp@rhreflex.com (Berfay)
  2. markovski@rhreflex.com (Markovski)
  3. nicolas@perspectivia.fr (Nicolas)

- **Pièces jointes** : 8 fichiers Excel + 1 PowerPoint
  - *(Mêmes 8 fichiers Excel que Workflow 1)*
  - **Rapport_PERSPECTIVIA.pptx** ✨

---

## 🚀 Déclenchement Manuel

### Via GitHub Actions Web Interface
1. Aller sur https://github.com/Bisiaux-dev/FAC/actions
2. Sélectionner le workflow souhaité :
   - "Workflow 1 - Email SANS PowerPoint"
   - "Workflow 2 - Email AVEC PowerPoint"
3. Cliquer sur "Run workflow"
4. Confirmer

### Via GitHub CLI
```bash
# Workflow 1 (sans PowerPoint)
gh workflow run "workflow1_sans_powerpoint.yml" --repo Bisiaux-dev/FAC

# Workflow 2 (avec PowerPoint)
gh workflow run "workflow2_avec_powerpoint.yml" --repo Bisiaux-dev/FAC
```

---

## 💻 Exécution Locale avec Confirmation

Pour exécuter localement avec confirmation des destinataires :

```bash
python launch_email.py
```

Le script affichera :
- Le workflow sélectionné
- La liste complète des destinataires
- Les pièces jointes qui seront envoyées
- Une demande de confirmation avant l'envoi

---

## 🔐 Secrets GitHub Requis

Les secrets suivants doivent être configurés dans les GitHub Secrets :

- `SMTP_USERNAME` : Adresse email Gmail (bisiauxpierre2@gmail.com)
- `SMTP_PASSWORD` : Mot de passe d'application Gmail
- `SHAREPOINT_USERNAME` : (Optionnel) Pour SharePoint privé
- `SHAREPOINT_PASSWORD` : (Optionnel) Pour SharePoint privé

### Vérifier les secrets
```bash
gh secret list --repo Bisiaux-dev/FAC
```

---

## 📊 Processus d'Exécution

Chaque workflow suit les étapes suivantes :

1. **Téléchargement** : Récupère le fichier Excel depuis SharePoint via Selenium
2. **Traitement** : Génère les 8 checklists Excel avec `t.py`
3. **Envoi** : Envoie l'email aux destinataires appropriés
4. **Archivage** : Conserve les fichiers générés pendant 7 jours

---

## 📁 Structure des Fichiers

```
FAC/
├── .github/workflows/
│   ├── workflow1_sans_powerpoint.yml    # Workflow 1
│   └── workflow2_avec_powerpoint.yml    # Workflow 2
├── email_sender/
│   ├── send_report_without_ppt.py       # Script workflow 1
│   └── send_report_with_ppt.py          # Script workflow 2
├── email_config/
│   └── email_settings.py                # Configuration email
├── launch_email.py                       # Script interactif local
├── download_robot.py                     # Téléchargement SharePoint
└── t.py                                  # Traitement des données
```

---

## 🎯 Contenu des Emails

Les emails contiennent :
- **Sujet** : Rapport PERSPECTIVIA - Checklists par équipe (DATE)
- **Corps** : Statistiques détaillées par équipe (Commercial, Admin, Comptabilité)
- **Format** : HTML avec mise en forme colorée + version texte brut

### Exemple de statistiques envoyées :
- Commercial : X dossiers (signatures manquantes)
- Dépôt client : X dossiers (dépôt à effectuer par client)
- Admin dépôt initial : X dossiers (brouillon)
- Admin vérif dépôt : X dossiers (dépôt OPCO)
- Cindy : X dossiers (facturation PEC)
- Facturation en retard : X dossiers (échéance 2)
- Trésorerie en retard : X dossiers (facturé >3 mois)
- **TOTAL : X dossiers à traiter**

---

## 🛠️ Maintenance

### Modifier les destinataires

**Workflow 1** : Modifier `email_config/email_settings.py`
```python
RECIPIENTS_CONFIG = {
    'to_emails': [
        # Liste des 12 emails
    ],
}
```

**Workflow 2** : Modifier `email_sender/send_report_with_ppt.py`
```python
WORKFLOW_2_RECIPIENTS = [
    'b.hunalp@rhreflex.com',
    'markovski@rhreflex.com',
    'nicolas@perspectivia.fr',
]
```

### Changer l'heure d'exécution

Modifier le cron dans les fichiers `.github/workflows/*.yml` :
```yaml
schedule:
  - cron: '0 7 * * *'  # 7h UTC = 8h Paris (hiver)
```

---

## 📝 Notes

- Les deux workflows s'exécutent **indépendamment** chaque jour
- Les fichiers générés sont conservés 7 jours dans les artifacts GitHub Actions
- Le système de retry automatique tente 3 fois l'envoi en cas d'échec
- Les logs détaillés sont disponibles dans GitHub Actions

---

## 🆘 Support

Pour toute question technique, contacter : **bisiaux.pierre@outlook.fr**
