# FAC PERSPECTIVIA - Automatisation Email

## 🎯 Objectif

Envoi automatique quotidien à **8h00** d'un email avec les statistiques des checklists PERSPECTIVIA.

## 📧 Email automatique

### Destinataires (12 personnes)

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

### Contenu de l'email

- **Format HTML** avec titres en **gras** (COMMERCIAL, ADMINISTRATIF, COMPTABILITÉ)
- **6 fichiers CSV** en pièces jointes
- **Statistiques** dynamiques depuis `checklist_recap.csv`

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
│   └── daily_report.yml       # GitHub Actions
├── email_sender/
│   ├── send_report_safe.py    # Script d'envoi
│   └── __init__.py
├── email_config/
│   ├── email_settings.py      # Configuration
│   └── __init__.py
├── Checklist/
│   ├── checklist_*.csv        # Checklists
│   └── checklist_recap.csv    # Récapitulatif
├── t.py                       # Génération données
└── requirements.txt           # Dépendances Python
```

## ⚙️ Configuration

### Secrets GitHub

Deux secrets sont configurés :
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
```

## 📊 Monitoring

- **Actions** : https://github.com/Bisiaux-dev/FAC/actions
- **Logs** : Voir les détails de chaque exécution
- **Artifacts** : Fichiers générés téléchargeables (7 jours)

## 🔐 Sécurité

- ✅ Mots de passe stockés dans les secrets GitHub
- ✅ Variables d'environnement utilisées
- ✅ Jamais affichés dans les logs

## 📧 Support

**Contact** : bisiaux.pierre@outlook.fr
