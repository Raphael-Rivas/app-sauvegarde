Deux applications, client et serveur.

Le client se connecte au serveur avec l'adresse IP du serveur par des sockets.

Quand le client arrive, il a le choix entre créer un compte et se connecter.

Quand il se crée un compte, il crée un ID (unique) et un mot de passe.

Si c'est la première fois qu'il se connecte, le serveur crée en local un dossier au nom de l'ID du client avec un fichier de paramètre à l'intérieur.

Le client a alors trois options : 
 - paramètres, 
 - sauvegarder, 
 - restaurer.
 
Paramètres 
-> le fichier où les types de fichiers (suffixes) à sauvegarder son marqués
-> le client envoie '+' ou '-' associé à un suffixe pour le rajouter ou l'enlever de la liste 

Sauvegarder 
-> le client passe en paramètre de l'appel le dossier à sauvegarder 
-> le serveur sauvegarde les fichiers s'ils n'ont jamais été sauvegardés, sinon vérifie s'ils ont été modifiés (avec la date de modif) avant de les enregistrer
-> recrée l'architecture d'origine

Restaurer 
-> le client passe en paramètre l'endroit où il veut stocker les fichiers ainsi que le fichier/dossier qu'il veut récupérer
-> option de récupération sans paramètre qui restaure facilement

En Python pour la facilité d'utilisation des Sockets. 
