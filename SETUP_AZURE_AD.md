# Configuration Azure AD pour SharePoint Downloader

## 🎯 Objectif

Permettre au workflow GitHub Actions de télécharger automatiquement le fichier Excel depuis SharePoint via l'API Microsoft Graph.

---

## 📋 Étapes de configuration Azure AD

### 1. Créer une application Azure AD

1. Connectez-vous au **Portail Azure** : https://portal.azure.com
2. Allez dans **Azure Active Directory**
3. Cliquez sur **App registrations** (Inscriptions d'applications)
4. Cliquez sur **+ New registration** (Nouvelle inscription)

**Paramètres de l'application :**
- **Name** : `FAC-Perspectivia-SharePoint-Downloader`
- **Supported account types** : "Accounts in this organizational directory only"
- **Redirect URI** : Laisser vide
- Cliquez sur **Register**

### 2. Noter les informations importantes

Une fois l'application créée, notez ces informations (onglet **Overview**) :

- **Application (client) ID** : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Directory (tenant) ID** : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 3. Créer un secret client

1. Dans votre application, allez dans **Certificates & secrets**
2. Cliquez sur **+ New client secret**
3. **Description** : `GitHub Actions Secret`
4. **Expires** : `24 months` (ou selon votre politique de sécurité)
5. Cliquez sur **Add**
6. **⚠️ IMPORTANT** : Copiez immédiatement la **Value** du secret (elle ne sera plus visible)

### 4. Configurer les permissions API

1. Allez dans **API permissions**
2. Cliquez sur **+ Add a permission**
3. Sélectionnez **Microsoft Graph**
4. Sélectionnez **Application permissions** (PAS Delegated)
5. Ajoutez ces permissions :

**Permissions requises :**
- `Files.Read.All` - Lire tous les fichiers
- `Sites.Read.All` - Lire tous les sites SharePoint

6. Cliquez sur **Add permissions**
7. **⚠️ CRUCIAL** : Cliquez sur **Grant admin consent for [votre organisation]**
   - Cette étape nécessite des droits administrateur Azure AD
   - Sans cela, l'application ne pourra pas accéder aux fichiers

### 5. Vérifier les permissions

Après avoir accordé le consentement administrateur, vous devriez voir :
- ✅ Status : **Granted for [organisation]** (en vert)

---

## 🔐 Configuration des secrets GitHub

1. Allez sur votre dépôt GitHub : https://github.com/Bisiaux-dev/FAC
2. Allez dans **Settings** > **Secrets and variables** > **Actions**
3. Ajoutez ces **3 nouveaux secrets** :

| Secret Name | Value | Description |
|------------|-------|-------------|
| `AZURE_TENANT_ID` | `[votre tenant ID]` | ID du tenant Azure AD |
| `AZURE_CLIENT_ID` | `[votre client ID]` | ID de l'application Azure AD |
| `AZURE_CLIENT_SECRET` | `[votre client secret]` | Secret client généré |

**Secrets existants à conserver :**
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

---

## 🔍 Informations du fichier SharePoint

**URL du fichier :**
```
https://cfanice-my.sharepoint.com/:x:/g/personal/b_hunalp_rhreflex_com/EU3ys-Z0yutBt2ZsX2OtAIABRVINihppyXSB6hoDyH6WBw
```

**Décomposition de l'URL :**
- **Site SharePoint** : `cfanice-my.sharepoint.com`
- **Type** : `:x:` (fichier Excel)
- **Utilisateur** : `b.hunalp@rhreflex.com`
- **ID du fichier** : `EU3ys-Z0yutBt2ZsX2OtAIABRVINihppyXSB6hoDyH6WBw`
- **Nom du fichier** : `NOUVEAU FAC PERSPECTIVIA.xlsx`

Ces informations sont déjà configurées dans le script `fetch_sharepoint_file.py`.

---

## ✅ Vérification de la configuration

### Test en local (optionnel)

Avant de tester sur GitHub Actions, vous pouvez tester localement :

```bash
# Définir les variables d'environnement
set AZURE_TENANT_ID=votre-tenant-id
set AZURE_CLIENT_ID=votre-client-id
set AZURE_CLIENT_SECRET=votre-client-secret

# Installer les dépendances
pip install requests

# Exécuter le script
python sharepoint_downloader/fetch_sharepoint_file.py
```

### Test sur GitHub Actions

1. Allez dans **Actions** sur GitHub
2. Sélectionnez le workflow **"Envoi automatique rapport PERSPECTIVIA"**
3. Cliquez sur **Run workflow**
4. Vérifiez les logs :
   - ✅ Authentification Microsoft Graph API réussie
   - ✅ Téléchargement du fichier depuis SharePoint
   - ✅ Génération des checklists
   - ✅ Envoi de l'email

---

## 🔒 Sécurité

### Bonnes pratiques appliquées

- ✅ Utilisation de **secrets GitHub** (jamais en clair dans le code)
- ✅ Authentification via **OAuth2 Client Credentials Flow**
- ✅ Permissions **minimales** (lecture seule)
- ✅ Consentement administrateur requis
- ✅ Secret client avec expiration (24 mois)

### Permissions accordées

L'application peut uniquement :
- **Lire** les fichiers SharePoint/OneDrive
- **Aucune permission** d'écriture, modification ou suppression
- **Aucun accès** aux emails, calendriers, ou autres données

---

## 🆘 Dépannage

### Erreur : "Insufficient privileges"

**Cause** : Le consentement administrateur n'a pas été accordé

**Solution** :
1. Retournez dans Azure AD > App registrations > Votre app
2. Allez dans **API permissions**
3. Cliquez sur **Grant admin consent**

### Erreur : "Invalid client secret"

**Cause** : Le secret client a expiré ou est incorrect

**Solution** :
1. Créez un nouveau secret client dans Azure AD
2. Mettez à jour le secret `AZURE_CLIENT_SECRET` sur GitHub

### Erreur : "File not found"

**Cause** : Le fichier n'existe pas ou le lien de partage a changé

**Solution** :
1. Vérifiez que le lien SharePoint est toujours accessible
2. Vérifiez que le nom du fichier est correct : `NOUVEAU FAC PERSPECTIVIA.xlsx`
3. Si le lien a changé, mettez à jour l'ID dans les variables d'environnement

### Le fichier n'est pas téléchargé

**Causes possibles** :
1. Permissions insuffisantes (voir ci-dessus)
2. Lien de partage révoqué ou expiré
3. Fichier déplacé ou renommé

**Solution** :
1. Vérifiez les logs GitHub Actions
2. Vérifiez que l'utilisateur `b.hunalp@rhreflex.com` a toujours accès au fichier
3. Créez un nouveau lien de partage si nécessaire

---

## 📧 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs détaillés dans GitHub Actions
2. Vérifiez que toutes les permissions sont accordées dans Azure AD
3. Vérifiez que les 3 secrets sont correctement configurés sur GitHub

**Contact** : bisiaux.pierre@outlook.fr
