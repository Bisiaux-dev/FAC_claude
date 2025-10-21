#!/usr/bin/env python3
"""
Module de récupération automatique du fichier Excel depuis SharePoint
via Microsoft Graph API
"""

import os
import sys
import requests
from datetime import datetime

class SharePointDownloader:
    """Gestionnaire de téléchargement depuis SharePoint"""

    def __init__(self):
        # Configuration depuis les variables d'environnement
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')

        # Informations du fichier SharePoint
        self.user_email = os.getenv('SHAREPOINT_USER_EMAIL', 'b.hunalp@rhreflex.com')
        self.file_name = os.getenv('SHAREPOINT_FILE_NAME', 'NOUVEAU FAC PERSPECTIVIA.xlsx')

        # ID du fichier extrait de l'URL
        # URL format: https://cfanice-my.sharepoint.com/:x:/g/personal/USER/FILE_ID
        self.file_id = os.getenv('SHAREPOINT_FILE_ID', 'EU3ys-Z0yutBt2ZsX2OtAIABRVINihppyXSB6hoDyH6WBw')

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_path = os.path.join(self.base_dir, self.file_name)

        self.access_token = None

    def validate_config(self):
        """Valide la configuration"""
        missing = []
        if not self.tenant_id:
            missing.append('AZURE_TENANT_ID')
        if not self.client_id:
            missing.append('AZURE_CLIENT_ID')
        if not self.client_secret:
            missing.append('AZURE_CLIENT_SECRET')

        if missing:
            print(f"❌ ERREUR: Variables d'environnement manquantes: {', '.join(missing)}")
            return False

        return True

    def get_access_token(self):
        """Obtient un token d'accès via OAuth2 Client Credentials Flow"""
        print("🔐 Authentification Microsoft Graph API...")

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        try:
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get('access_token')

            if self.access_token:
                print("✅ Authentification réussie")
                return True
            else:
                print("❌ ERREUR: Token non reçu")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ ERREUR d'authentification: {e}")
            return False

    def download_file_by_sharing_link(self):
        """Télécharge le fichier via le lien de partage"""
        print(f"📥 Téléchargement du fichier: {self.file_name}...")

        # Méthode 1: Via lien de partage
        # Encode le lien de partage en base64
        sharing_url = f"https://cfanice-my.sharepoint.com/:x:/g/personal/{self.user_email.replace('@', '_').replace('.', '_')}/{self.file_id}"

        # Encode l'URL pour Graph API
        import base64
        encoded_url = base64.b64encode(sharing_url.encode()).decode()
        # Remplace les caractères pour format Graph API
        encoded_url = encoded_url.rstrip('=').replace('/', '_').replace('+', '-')

        # URL de l'API Graph pour récupérer le fichier partagé
        api_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        try:
            # Récupère les métadonnées du fichier
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()

            file_metadata = response.json()
            download_url = file_metadata.get('@microsoft.graph.downloadUrl')

            if not download_url:
                print("❌ ERREUR: URL de téléchargement non trouvée")
                return False

            # Télécharge le fichier
            print(f"⬇️  Téléchargement depuis SharePoint...")
            file_response = requests.get(download_url, timeout=60)
            file_response.raise_for_status()

            # Sauvegarde le fichier
            with open(self.output_path, 'wb') as f:
                f.write(file_response.content)

            file_size = len(file_response.content)
            print(f"✅ Fichier téléchargé: {self.output_path} ({file_size:,} octets)")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ ERREUR de téléchargement: {e}")
            return False

    def download_file_by_drive_path(self):
        """Télécharge le fichier via le chemin OneDrive (méthode alternative)"""
        print(f"📥 Téléchargement alternatif via OneDrive...")

        # Convertit l'email en format OneDrive
        user_id = self.user_email.replace('@', '_').replace('.', '_')

        # URL pour accéder au fichier dans le OneDrive de l'utilisateur
        api_url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/drive/root:/{self.file_name}:/content"

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            response = requests.get(api_url, headers=headers, timeout=60)
            response.raise_for_status()

            # Sauvegarde le fichier
            with open(self.output_path, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content)
            print(f"✅ Fichier téléchargé: {self.output_path} ({file_size:,} octets)")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ ERREUR de téléchargement: {e}")
            return False

    def download(self):
        """Fonction principale de téléchargement"""
        print("=" * 60)
        print("SHAREPOINT DOWNLOADER - Microsoft Graph API")
        print("=" * 60)

        if not self.validate_config():
            return False

        if not self.get_access_token():
            return False

        # Essaie d'abord via le lien de partage
        if self.download_file_by_sharing_link():
            return True

        # Si échec, essaie via le chemin OneDrive
        print("\n⚠️  Tentative via chemin OneDrive...")
        if self.download_file_by_drive_path():
            return True

        print("\n❌ ÉCHEC: Impossible de télécharger le fichier")
        print("\nℹ️  Vérifiez:")
        print("   1. Les permissions de l'application Azure AD")
        print("   2. Le lien de partage est toujours valide")
        print("   3. Le nom du fichier est correct")
        return False


def main():
    """Point d'entrée principal"""
    downloader = SharePointDownloader()
    success = downloader.download()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
