# 📚 Guide Git & GitHub Actions - Projet FAC_claude

> **Repository:** https://github.com/Bisiaux-dev/FAC_claude
> **Automatisation:** SharePoint → XLSX → Analyse de données
> **Dernière mise à jour:** 2025-10-24

---

## 🔗 Informations Git

### Repository
- **URL HTTPS:** https://github.com/Bisiaux-dev/FAC_claude
- **URL SSH:** git@github.com:Bisiaux-dev/FAC_claude.git
- **Propriétaire:** Bisiaux-dev
- **Nom du repo:** FAC_claude
- **Branche principale:** `main`

### Commandes Git essentielles

```bash
# Vérifier le remote configuré (IMPORTANT avant tout push)
git remote -v
# Doit afficher: https://github.com/Bisiaux-dev/FAC_claude

# Vérifier l'état du repository
git status

# Voir l'historique des commits
git log --oneline -10

# Voir les différences
git diff                    # Changements non staged
git diff --staged          # Changements staged

# Ajouter des fichiers
git add .                  # Tous les fichiers
git add fichier.py         # Fichier spécifique

# Committer
git commit -m "Message descriptif"

# Pousser vers GitHub
git push origin main

# Récupérer les dernières modifications
git pull origin main

# Annuler des changements locaux
git checkout -- fichier.py  # Annuler les modifications d'un fichier
git reset HEAD fichier.py   # Unstage un fichier
```

---

## 🚀 GitHub Actions - Workflow

### Fichier de configuration
**Emplacement:** `.github/workflows/sharepoint.yml`

### Workflow actuel

```yaml
name: SharePoint XLSX Automation

on:
  schedule:
    - cron: '0 8 * * *'    # Tous les jours à 8h UTC (9h/10h Paris)
  workflow_dispatch:        # Lancement manuel
```

**Déclencheurs:**
1. **Automatique:** Tous les jours à 8h00 UTC
2. **Manuel:** Via l'interface GitHub Actions

---

## 🎮 Commandes GitHub CLI (gh)

### Installation et authentification

```bash
# Vérifier l'authentification
gh auth status

# Se connecter (si nécessaire)
gh auth login

# Vérifier l'accès au repository
gh repo view Bisiaux-dev/FAC_claude
```

### Gestion des workflows

```bash
# Lister les workflows disponibles
gh workflow list

# Lancer le workflow manuellement
gh workflow run sharepoint.yml

# Voir les exécutions récentes
gh run list --limit 10

# Voir le statut de la dernière exécution
gh run list --limit 1

# Voir les détails d'une exécution
gh run view <RUN_ID>

# Voir les logs d'une exécution
gh run view <RUN_ID> --log

# Télécharger les artifacts
gh run download <RUN_ID>

# Annuler une exécution en cours
gh run cancel <RUN_ID>

# Relancer une exécution échouée
gh run rerun <RUN_ID>
```

### Monitoring en temps réel

```bash
# Surveiller l'exécution en cours
gh run watch

# Vérifier les workflows en cours
gh run list --status in_progress

# Vérifier les workflows réussis aujourd'hui
gh run list --status success --limit 5

# Vérifier les workflows échoués
gh run list --status failure --limit 5
```

---

## 📊 Étapes du Workflow

### 1. Checkout (actions/checkout@v3)
Clone le repository dans l'environnement GitHub Actions.

### 2. Setup Python (actions/setup-python@v4)
- Version: Python 3.11
- Installe pip

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dépendances:**
```
selenium>=4.15.0
pandas>=2.0.0
openpyxl>=3.0.0
matplotlib>=3.8.0
numpy>=1.24.0
```

### 4. Install Chrome and ChromeDriver
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

### 5. Run SharePoint scraper
```bash
python scraper.py
```
**Variables d'environnement:**
- `HEADLESS: true` (mode sans interface graphique)

**Sortie:**
- `downloads/NOUVEAU FAC PERSPECTIVIA.xlsx` (224 KB)

### 6. Run data processing
```bash
python pt2.py
```

**Sorties:**
- `output/Données_transformé/` - CSV transformés (30 fichiers)
- `output/Checklist/` - 8 checklists (CSV + récap)
- `output/Graphiques/` - 7 graphiques PNG

### 7. Upload artifacts
Les artifacts sont conservés **90 jours** par défaut.

**5 artifacts créés:**
1. `downloaded-xlsx` - Fichier XLSX source
2. `logs` - Logs d'exécution (*.log)
3. `screenshots` - Screenshots debug (*.png)
4. `processed-data` - Toutes les données transformées
5. `graphs` - Graphiques PNG

---

## 📈 Métriques du Workflow

### Performance typique

| Métrique | Valeur |
|----------|--------|
| Durée totale | ~2m15s |
| Temps de setup | ~40s |
| Temps de scraping | ~15s |
| Temps de processing | ~20s |
| Temps d'upload | ~60s |

### Utilisation des ressources

- **OS:** Ubuntu 24.04
- **CPU:** 2 cores
- **RAM:** 7 GB
- **Disk:** 14 GB
- **Coût:** Gratuit (GitHub Actions minutes incluses)

### Limites GitHub Actions

- **Minutes/mois (gratuit):** 2000 min
- **Minutes/exécution:** ~2.5 min
- **Exécutions/mois possibles:** ~800
- **Exécutions/jour (actuel):** 1 (8h UTC)
- **Marge restante:** Large ✅

---

## 🔍 Logs et Debugging

### Structure des logs

```
[TIMESTAMP] - [LEVEL] - [MESSAGE]
2025-10-24 10:12:20 - INFO - Setting up Chrome WebDriver...
```

**Niveaux de logs:**
- `INFO` - Information normale
- `WARNING` - Avertissement
- `ERROR` - Erreur

**Emojis dans les logs (pt2.py):**
- ✓ - Succès
- ✗ - Erreur
- ⚠ - Warning
- 📊 - Graphiques
- 📋 - Checklists
- 📈 - Données
- 💰 - CA/Finances
- 📚 - PROMO

### Consulter les logs

```bash
# Logs complets d'une exécution
gh run view <RUN_ID> --log

# Filtrer les logs (exemples)
gh run view <RUN_ID> --log | grep ERROR
gh run view <RUN_ID> --log | grep -E "(✓|✗|⚠)"
gh run view <RUN_ID> --log | grep "Download successful"
gh run view <RUN_ID> --log | grep "CA Summary"
```

### Screenshots de debug

En cas d'erreur, les screenshots sont automatiquement capturés:
- `screenshot_01_download_initiated_YYYYMMDD_HHMMSS.png`
- `screenshot_error_final_YYYYMMDD_HHMMSS.png`

Téléchargement: Artifact `screenshots`

---

## 📦 Artifacts

### Télécharger les artifacts

**Méthode 1: GitHub CLI**
```bash
# Télécharger tous les artifacts
gh run download <RUN_ID>

# Télécharger un artifact spécifique
gh run download <RUN_ID> -n processed-data
gh run download <RUN_ID> -n graphs
```

**Méthode 2: Interface Web**
1. Aller sur https://github.com/Bisiaux-dev/FAC_claude/actions
2. Cliquer sur l'exécution désirée
3. Scroller en bas → Section "Artifacts"
4. Cliquer sur le nom de l'artifact pour télécharger

### Contenu des artifacts

#### 1. `downloaded-xlsx`
```
NOUVEAU FAC PERSPECTIVIA.xlsx (224 KB)
```

#### 2. `logs`
```
sharepoint_scraper_YYYYMMDD_HHMMSS.log
```

#### 3. `screenshots`
```
screenshot_01_download_initiated_YYYYMMDD_HHMMSS.png
screenshot_error_final_YYYYMMDD_HHMMSS.png (si erreur)
```

#### 4. `processed-data` (30 fichiers)
```
output/
├── Données_transformé/
│   ├── NOUVEAU FAC PERSPECTIVIA.csv
│   ├── NOUVEAU FAC PERSPECTIVIA_Vague_2025V1.csv
│   ├── NOUVEAU FAC PERSPECTIVIA_Vague_2025V2.csv
│   ├── NOUVEAU FAC PERSPECTIVIA_Vague_2025V3.csv
│   ├── Données_Transformées.csv
│   ├── Statuts_Intermédiaires.csv
│   └── PROMO_Réél_par_Vague.csv
└── Checklist/
    ├── checklist_cindy.csv
    ├── checklist_admin_dépôt_initial.csv
    ├── checklist_admin_vérifier_dépôt.csv
    ├── checklist_équipe_commercial.csv
    ├── dépôt_que_le_client_doit_effectuer.csv
    ├── checklist_facturation_en_retard.csv
    ├── tresorerie_en_retard.csv
    └── checklist_recap.csv
```

#### 5. `graphs` (7 fichiers PNG)
```
output/Graphiques/
├── Paiements_par_Vague.png
├── Statut_Formations_par_Vague.png
├── CA_par_Catégorie_Toutes_Vagues.png
├── Statuts_Intermédiaires_Reel.png
├── Statuts_Intermédiaires_Previsionnel.png
├── Statuts_Intermédiaires_Potentiel.png
└── PROMO_Reel_par_Vague.png
```

---

## 🔐 Secrets et Variables

### Secrets GitHub (si nécessaire)

Pour ajouter des secrets (ex: credentials SharePoint):

```bash
# Via GitHub CLI
gh secret set SECRET_NAME

# Ou via l'interface web
Settings → Secrets and variables → Actions → New repository secret
```

**Secrets recommandés (non utilisés actuellement):**
- `SHAREPOINT_URL` - URL du fichier SharePoint
- `SMTP_USERNAME` - Email pour notifications
- `SMTP_PASSWORD` - Mot de passe email

### Variables d'environnement

**Actuellement utilisées:**
```yaml
env:
  HEADLESS: true  # Mode sans interface pour Selenium
```

---

## 🛠️ Troubleshooting

### Problème 1: Workflow échoue

```bash
# Consulter les logs
gh run view <RUN_ID> --log | tail -100

# Identifier l'étape échouée
gh run view <RUN_ID>

# Relancer l'exécution
gh run rerun <RUN_ID>
```

### Problème 2: Mauvais repository

```bash
# Vérifier le remote
git remote -v

# Si incorrect, changer
git remote set-url origin https://github.com/Bisiaux-dev/FAC_claude
```

### Problème 3: Conflit de commits

```bash
# Récupérer les dernières modifications
git pull origin main

# Résoudre les conflits manuellement
# Puis
git add .
git commit -m "Resolve conflicts"
git push origin main
```

### Problème 4: Workflow en attente

```bash
# Vérifier les workflows en cours
gh run list --status queued

# Annuler si nécessaire
gh run cancel <RUN_ID>
```

---

## 📅 Planning et Scheduling

### Configuration actuelle

```yaml
schedule:
  - cron: '0 8 * * *'  # Tous les jours à 8h00 UTC
```

**Équivalence heure locale:**
- **Hiver (UTC+1):** 9h00 Paris
- **Été (UTC+2):** 10h00 Paris

### Modifier le planning

Pour changer l'heure d'exécution, éditer `.github/workflows/sharepoint.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'   # 6h00 UTC = 7h00/8h00 Paris
  - cron: '0 12 * * *'  # 12h00 UTC = 13h00/14h00 Paris
  - cron: '0 18 * * *'  # 18h00 UTC = 19h00/20h00 Paris
```

**Syntaxe cron:**
```
┌───────────── minute (0 - 59)
│ ┌───────────── heure (0 - 23)
│ │ ┌───────────── jour du mois (1 - 31)
│ │ │ ┌───────────── mois (1 - 12)
│ │ │ │ ┌───────────── jour de la semaine (0 - 6) (Dimanche=0)
│ │ │ │ │
* * * * *
```

**Exemples:**
- `0 8 * * *` - Tous les jours à 8h
- `0 8 * * 1-5` - Du lundi au vendredi à 8h
- `0 */6 * * *` - Toutes les 6 heures
- `0 8,14 * * *` - À 8h et 14h

---

## 📊 Monitoring et Alertes

### Vérification manuelle quotidienne

```bash
# Vérifier la dernière exécution
gh run list --limit 1

# Si succès
# ✓ completed  success  SharePoint XLSX Automation

# Si échec
# ✗ completed  failure  SharePoint XLSX Automation
```

### Notifications par email (optionnel)

Pour recevoir des notifications:
1. GitHub → Settings → Notifications
2. Cocher "Actions" dans Email notifications
3. Choisir: "Only notify for failed workflows"

---

## 📝 Bonnes pratiques

### Commits

1. **Messages descriptifs:**
   ```bash
   # ✓ Bon
   git commit -m "Fix: Correct download URL parameter for SharePoint"

   # ✗ Mauvais
   git commit -m "fix"
   ```

2. **Types de commits:**
   - `Fix:` - Correction de bug
   - `Update:` - Mise à jour fonctionnalité
   - `Add:` - Nouvelle fonctionnalité
   - `Remove:` - Suppression
   - `Refactor:` - Refactorisation

3. **Co-authorship (Claude Code):**
   ```bash
   git commit -m "Fix: Issue description

   🤖 Generated with Claude Code

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

### Workflows

1. **Tester localement d'abord** (si possible)
2. **Vérifier les logs** après chaque exécution
3. **Ne pas commit de secrets** dans le code
4. **Utiliser des chemins relatifs** (compatibilité multi-OS)
5. **Documenter les changements** dans les commits

### Branches

**Stratégie actuelle:** Branche unique `main`

**Si développement futur:**
```bash
# Créer une branche de développement
git checkout -b dev/nouvelle-fonctionnalite

# Travailler sur la branche
git add .
git commit -m "Add: Nouvelle fonctionnalité"

# Pousser la branche
git push -u origin dev/nouvelle-fonctionnalite

# Créer une Pull Request via GitHub
gh pr create --title "Nouvelle fonctionnalité" --body "Description"

# Merger après validation
gh pr merge
```

---

## 🔗 Liens utiles

### Documentation

- **GitHub Actions:** https://docs.github.com/en/actions
- **GitHub CLI:** https://cli.github.com/manual/
- **Git:** https://git-scm.com/doc
- **Repository:** https://github.com/Bisiaux-dev/FAC_claude

### Workflows

- **Actions page:** https://github.com/Bisiaux-dev/FAC_claude/actions
- **Workflow file:** https://github.com/Bisiaux-dev/FAC_claude/blob/main/.github/workflows/sharepoint.yml
- **Latest run:** https://github.com/Bisiaux-dev/FAC_claude/actions/runs/latest

### Support

- **GitHub Status:** https://www.githubstatus.com/
- **GitHub Community:** https://github.community/
- **Issues:** https://github.com/Bisiaux-dev/FAC_claude/issues

---

## 🎯 Checklist de vérification

### Avant chaque commit

- [ ] `git status` - Vérifier les fichiers modifiés
- [ ] `git remote -v` - Vérifier le repository
- [ ] Tester localement (si possible)
- [ ] Message de commit descriptif
- [ ] Pas de secrets dans le code

### Après chaque push

- [ ] Vérifier que le push a réussi
- [ ] Attendre la fin du workflow (si automatique)
- [ ] Vérifier les logs en cas d'échec
- [ ] Télécharger les artifacts pour validation

### Maintenance hebdomadaire

- [ ] Vérifier les workflows de la semaine
- [ ] Analyser les métriques (durée, succès)
- [ ] Nettoyer les anciens artifacts (automatique après 90j)
- [ ] Vérifier les mises à jour des dépendances

---

## 📞 Contact et Support

**Maintainer:** Bisiaux Pierre
**Email:** bisiaux.pierre@outlook.fr
**Repository:** https://github.com/Bisiaux-dev/FAC_claude

---

*Dernière mise à jour: 2025-10-24*
*Version: 1.0.0*
