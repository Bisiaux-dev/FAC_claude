# FAC PERSPECTIVIA - Automatisation Email

## 🎯 Objectif

**Workflow 100% autonome** qui :
1. 📥 Télécharge automatiquement le fichier Excel depuis SharePoint
2. 📊 Génère les checklists à partir des données
3. 📧 Envoie un email quotidien à **8h00** avec les statistiques

## 📧 Email automatique

### Destinataires (3 personnes)

1. bisiaux.pierre@outlook.fr
2. C.romeo@planBgroupe.com
3. b.hunalp@rhreflex.com

### Contenu de l'email

- **Format HTML** avec titres en **gras** (COMMERCIAL, ADMINISTRATIF, COMPTABILITÉ)
- **6 fichiers Excel (.xlsx)** en pièces jointes
- **Statistiques** dynamiques depuis `checklist_recap.xlsx`

### Statistiques envoyées

- Commercial : X dossiers
- Admin dépôt initial : X dossiers
- Admin vérif dépôt : X dossiers
- Cindy (facturation) : X dossiers
- Facturation en retard : X dossiers
- **TOTAL** : X dossiers

## 🚀 Utilisation

### Envoi manuel

```bash
python email_sender/send_report_safe.py
```

### Automatisation GitHub Actions

L'email est envoyé automatiquement tous les jours à **8h00** (heure de Paris).

**Workflow** : `.github/workflows/daily_report.yml`

### Test immédiat

Sur GitHub :
1. Aller dans **Actions**
2. Sélectionner "Envoi automatique rapport PERSPECTIVIA"
3. Cliquer sur **"Run workflow"**

## 📁 Structure

```
FAC/
├── .github/workflows/
│   └── daily_report.yml           # GitHub Actions
├── email_sender/
│   ├── send_report_safe.py        # Script d'envoi
│   └── __init__.py
├── email_config/
│   ├── email_settings.py          # Configuration
│   └── __init__.py
├── Checklist/
│   ├── checklist_*.xlsx           # Checklists générées
│   └── checklist_recap.xlsx       # Récapitulatif
├── download_robot.py              # Robot Selenium pour SharePoint
├── t.py                           # Génération données
├── requirements.txt               # Dépendances Python
└── README_FAC.md                  # Documentation
```

## ⚙️ Configuration

### Secrets GitHub

**4 secrets configurés :**

**Pour SharePoint (Selenium) :**
- `SHAREPOINT_USERNAME` : b.hunalp@rhreflex.com
- `SHAREPOINT_PASSWORD` : (mot de passe SharePoint)

**Pour l'envoi d'email :**
- `SMTP_USERNAME` : bisiauxpierre2@gmail.com
- `SMTP_PASSWORD` : (mot de passe Gmail)

### Modifier l'heure d'envoi

Éditer `.github/workflows/daily_report.yml` :

```yaml
schedule:
  - cron: '0 7 * * *'  # 8h Paris (7h UTC)
```

## 🔧 Dépendances

```
pandas>=2.0.0
openpyxl>=3.1.0
matplotlib>=3.7.0
python-pptx>=0.6.21
selenium>=4.15.0
```

## 📊 Monitoring

- **Actions** : https://github.com/Bisiaux-dev/FAC/actions
- **Logs** : Voir les détails de chaque exécution
- **Artifacts** : Fichiers générés téléchargeables (7 jours)

## 🔐 Sécurité

- ✅ Secrets stockés dans GitHub Secrets (jamais en clair)
- ✅ Authentification SharePoint avec Selenium
- ✅ Mode headless en CI/CD (aucune interface graphique)
- ✅ Variables d'environnement utilisées
- ✅ Aucun mot de passe affiché dans les logs

## 📧 Support

**Contact** : bisiaux.pierre@outlook.fr
