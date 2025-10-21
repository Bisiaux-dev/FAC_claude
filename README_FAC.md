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
├── sharepoint_downloader/
│   ├── fetch_sharepoint_file.py   # Téléchargement SharePoint
│   └── __init__.py
├── email_sender/
│   ├── send_report_safe.py        # Script d'envoi
│   └── __init__.py
├── email_config/
│   ├── email_settings.py          # Configuration
│   └── __init__.py
├── Checklist/
│   ├── checklist_*.xlsx           # Checklists générées
│   └── checklist_recap.xlsx       # Récapitulatif
├── t.py                           # Génération données
├── requirements.txt               # Dépendances Python
├── README_FAC.md                  # Documentation
└── SETUP_AZURE_AD.md              # Configuration Azure AD
```

## ⚙️ Configuration

### Secrets GitHub

**5 secrets configurés :**

**Pour SharePoint (Microsoft Graph API) :**
- `AZURE_TENANT_ID` : ID du tenant Azure AD
- `AZURE_CLIENT_ID` : ID de l'application Azure AD
- `AZURE_CLIENT_SECRET` : Secret client Azure AD

**Pour l'envoi d'email :**
- `SMTP_USERNAME` : bisiauxpierre2@gmail.com
- `SMTP_PASSWORD` : (mot de passe Gmail)

📋 **Configuration détaillée** : Voir [SETUP_AZURE_AD.md](SETUP_AZURE_AD.md)

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
requests>=2.31.0
```

## 📊 Monitoring

- **Actions** : https://github.com/Bisiaux-dev/FAC/actions
- **Logs** : Voir les détails de chaque exécution
- **Artifacts** : Fichiers générés téléchargeables (7 jours)

## 🔐 Sécurité

- ✅ Secrets stockés dans GitHub Secrets (jamais en clair)
- ✅ Authentification OAuth2 avec Azure AD
- ✅ Permissions minimales (lecture seule SharePoint)
- ✅ Variables d'environnement utilisées
- ✅ Aucun mot de passe affiché dans les logs

## 📧 Support

**Contact** : bisiaux.pierre@outlook.fr
