# Application de sauvegarde client-serveur (Python, sockets)

**Contributeurs :** Raphaël RIVAS, Maël NICOLAS

**Dépôt Git :** https://gitlabinfo.iutmontp.univ-montp2.fr/continuite-services-s5/app-sauvegarde

Application client-serveur permettant de sauvegarder et restaurer des fichiers via une connexion réseau TCP.

## Fonctionnalités implémentées

### Authentification
- **Inscription (Sign up)** : Création d'un compte avec identifiant et mot de passe (hashé en SHA-256)
- **Connexion (Log in)** : Authentification avec identifiant et mot de passe
- Le serveur crée un dossier dédié par utilisateur pour stocker ses fichiers

### Sauvegarde
- **Sauvegarde de fichiers** : Sélection de fichiers individuels via une boîte de dialogue
- **Sauvegarde de dossier** : Sélection d'un dossier complet (récursif, tous les fichiers sont sauvegardés)
- L'arborescence d'origine est recréée côté serveur

### Restauration
- **Restauration complète (all)** : Restaure tous les fichiers de l'utilisateur
- **Restauration de fichier (file)** : Restaure un ou plusieurs fichiers par leur nom
- **Restauration de dossier (directory)** : Restaure un dossier spécifique et son contenu
- Affichage de l'arborescence des fichiers disponibles avant restauration

## Utilisation

### Configuration
Créer un fichier `.env` avec :
```
HOST=<adresse_ip_serveur>
PORT=<port>
SERVER_PATH=<chemin_stockage_serveur>  # côté serveur uniquement
```

### Commandes client
1. Lancer le client : `python client.py`
2. Choisir `log` (connexion) ou `sign` (inscription)
3. Choisir une action : `save`, `restore`, `settings`, `exit`

## Écarts par rapport aux attentes

### Non implémenté

| Fonctionnalité | Attendu | État actuel |
|----------------|---------|-------------|
| **Filtrage par suffixes** | Sauvegarde uniquement les fichiers dont les suffixes sont dans un fichier de paramètres | **Non implémenté** - Tous les fichiers sont sauvegardés |
| **Sauvegarde incrémentale** | Ne copier que les fichiers nouveaux ou modifiés depuis la dernière sauvegarde | **Non implémenté** - Tous les fichiers sont renvoyés à chaque sauvegarde |
| **Détection première sauvegarde** | Différencier première sauvegarde vs sauvegardes suivantes | **Non implémenté** |
| **Option Settings** | Interface pour modifier les paramètres (suffixes) | **Non implémenté** |

### Options non implémentées (bonus)

| Fonctionnalité | Description | État |
|----------------|-------------|------|
| **Sécurisation des flux (TLS)** | Chiffrement des communications réseau | **Non implémenté** - Connexion TCP en clair |
| **Chiffrement des données** | Chiffrement des fichiers stockés côté serveur | **Non implémenté** - Fichiers stockés en clair |

## Architecture technique

### Client (`client.py`)
- Connexion socket TCP au serveur
- Interface en ligne de commande + boîtes de dialogue (tkinter) pour sélection des fichiers/dossiers
- Envoi des fichiers avec taille préfixée (10 octets) + marqueur de fin "end"

### Serveur (`server.py`)
- Serveur multi-threadé (un thread par client)
- Stockage des fichiers dans `SERVER_PATH/<username>/`
- Mot de passe hashé stocké dans `password.txt` par utilisateur

## TODO pour conformité complète

1. [ ] Implémenter le fichier de paramètres (liste de suffixes autorisés)
2. [ ] Ajouter le filtrage des fichiers par suffixe côté client
3. [ ] Implémenter la détection de sauvegarde existante (comparaison par date de modification)
4. [ ] Implémenter la sauvegarde incrémentale
5. [ ] Ajouter l'interface "Settings" pour gérer les suffixes
6. [ ] (Option) Sécuriser les connexions avec TLS
7. [ ] (Option) Chiffrer les fichiers stockés côté serveur
