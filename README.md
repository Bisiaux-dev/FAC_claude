# 🤖 CRM Automation - GitHub Actions Scheduler

**Version**: 0.1 - GitHub Actions Edition
**Système original**: CRM_Automation_v2.3 (Robot Framework)
**Modification**: Remplacement du scheduler Windows par GitHub Actions

---

## 🎯 Vue d'ensemble

Ce projet utilise le **système d'automatisation CRM fonctionnel existant** (Robot Framework + Python) et remplace uniquement le scheduler Windows par **GitHub Actions** pour une exécution automatique dans le cloud.

### ✅ Ce qui est conservé (fonctionne déjà parfaitement)

- ✅ **Robot Framework** pour l'extraction CRM (cf_extract.robot, cip_extract.robot)
- ✅ **Scripts Python** pour la génération PowerPoint (scripts/create_powerpoint_final.py)
- ✅ **Parsing SVG** (scripts/parse_svg_data.py)
- ✅ **Envoi email** (email_sender.py)
- ✅ **Toute la logique d'extraction** (11 graphiques CF + CIP)

### 🔄 Ce qui change

- ❌ **Ancien**: Scheduler Windows (8h00/16h00/3min - conflits multiples)
- ✅ **Nouveau**: GitHub Actions (18h00 UTC, Lun-Ven)

---

## 📋 Prérequis

- Compte GitHub
- Credentials CRM
- Email Gmail (pour SMTP)

---

## 🚀 Installation (10 minutes)

### 1️⃣ Pousser le code sur GitHub

```powershell
# Déjà fait si tu as suivi les étapes précédentes
cd C:\Users\Pierre\Desktop\rs_crm_automation_V0.1
git add .
git commit -m "Add Robot Framework files"
git push origin main
```

### 2️⃣ Configurer les Secrets GitHub

Va sur : https://github.com/Bisiaux-dev/crm-automation/settings/secrets/actions

Ajoute ces **10 secrets** (un par un) :

#### CRM (5 secrets)
```
CRM_BASE_URL = crm.isimcrm.fr
CRM_USERNAME = 123123@123.fr
CRM_PASSWORD = 123123@123.fr
CRM_HTTP_AUTH_USER = crm_isim
CRM_HTTP_AUTH_PASSWORD = ihJer3tZT22uKUfa
```

#### Email (5 secrets)
```
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = bisiauxpierre2@gmail.com
SMTP_PASSWORD = owlg osev vszn fuyp
EMAIL_RECIPIENTS = bisiaux.pierre@outlook.fr,C.romeo@planBgroupe.com,b.hunalp@rhreflex.com
```

### 3️⃣ Tester manuellement

1. Va sur : https://github.com/Bisiaux-dev/crm-automation/actions
2. Clique sur **"CRM Daily Automation (Original System)"**
3. Clique sur **"Run workflow"**
4. Attends 10-15 minutes

---

## 📅 Planification automatique

Le workflow s'exécute automatiquement :
- **⏰ Heure** : 18h00 UTC (19h00 Paris hiver, 20h00 été)
- **📆 Jours** : Lundi au Vendredi
- **🔄 Processus** :
  1. Installation Robot Framework + Python
  2. Installation Chrome + ChromeDriver
  3. Extraction CF (cf_extract.robot)
  4. Extraction CIP (cip_extract.robot)
  5. Génération PowerPoint (create_powerpoint_final.py)
  6. Envoi email (email_sender.py)

---

## 📊 Workflow détaillé

### Étape 1 : Extraction CF (5 graphiques)
```
- Jour-J : 2 graphiques (jourj_graph2.svg, jourj_graph4.svg)
- Semaine précédente : 2 graphiques (semaine_precedente_graph3.svg, semaine_precedente_graph4.svg)
- J-90 : 1 graphique (j90_semaine_graph4.svg)
```

### Étape 2 : Extraction CIP (6 graphiques)
```
- J-7 à aujourd'hui : 3 graphiques (cip_j7_graph0/2/4.svg)
- Jour-J : 2 graphiques (cip_jourj_graph0/4.svg)
- J-90 à aujourd'hui : 1 graphique (cip_j90_graph0.svg)
```

### Étape 3 : Génération PowerPoint
```
- 12 slides de données + 1 slide titre
- Filtrage par organisation (ISIM / Perspectivia)
- Génération automatique des graphiques
```

### Étape 4 : Envoi Email
```
- Destinataires : 3 personnes
- Pièce jointe : Rapport PowerPoint
- Logs d'exécution inclus
```

---

## 📂 Structure du projet

```
rs_crm_automation_V0.1/
├── .github/workflows/
│   └── crm_daily_original.yml    # Workflow GitHub Actions
├── scripts/
│   ├── create_powerpoint_final.py  # Génération PowerPoint
│   └── parse_svg_data.py           # Parsing SVG
├── cf_extract.robot              # Extraction CF (Robot Framework)
├── cip_extract.robot             # Extraction CIP (Robot Framework)
├── config.robot                  # Configuration CRM (généré par workflow)
├── email_sender.py               # Envoi email
├── email_config.py               # Config email (générée par workflow)
└── requirements.txt              # Dépendances Python
```

---

## 🔧 Dépannage

### Workflow échoue avec "Chrome not found"
- **Solution** : Le workflow installe Chrome automatiquement, réessaye

### Workflow échoue avec "Authentication failed"
- **Solution** : Vérifie les secrets CRM dans GitHub Settings

### Email non reçu
- **Solution** : Vérifie SMTP_PASSWORD (doit être l'App Password Gmail)

### Extraction incomplète (moins de 11 SVG)
- **Solution** : Vérifie les logs Robot Framework dans les artifacts

---

## 📊 Artifacts disponibles

Après chaque exécution, tu peux télécharger :

1. **crm-report-XXX** : Rapport PowerPoint (stocké 30 jours)
2. **svg-data-XXX** : Fichiers SVG extraits (stockés 7 jours)
3. **robot-logs-XXX** : Logs Robot Framework (stockés 7 jours)

---

## 🎯 Avantages de cette solution

### ✅ Avantages
- Pas de serveur à maintenir
- Exécution fiable dans le cloud
- Logs et artifacts automatiques
- Gratuit (2000 minutes/mois)
- Pas de conflit de scheduler
- Notifications en cas d'échec

### 🔄 vs Ancien système
| Critère | Ancien | Nouveau |
|---------|--------|---------|
| **Scheduler** | Windows Task (multiples, conflictuels) | GitHub Actions (unique) |
| **Infrastructure** | PC Windows local | Cloud GitHub |
| **Maintenance** | Manuelle | Automatique |
| **Logs** | Fichiers locaux | GitHub Artifacts |
| **Coût** | PC allumé 24/7 | Gratuit |
| **Fiabilité** | Dépend du PC | 99.9% uptime |

---

## 📞 Support

- **Email** : bisiaux.pierre@outlook.fr
- **GitHub Issues** : https://github.com/Bisiaux-dev/crm-automation/issues
- **Logs** : Actions tab → Workflow run → Artifacts

---

## 🎉 C'est tout !

Ton système fonctionne maintenant automatiquement sur GitHub Actions !

**Prochaine exécution** : Prochain jour de semaine à 18h00 UTC

---

*Créé le 2025-01-13 pour Pierre Bisiaux*
