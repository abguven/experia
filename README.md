# 🔥 Experia

**Knowledge base dédiée aux Data Engineers**

Experia est une application Streamlit conçue pour centraliser, documenter et retrouver efficacement les problématiques techniques rencontrées lors du développement ou de l’intégration de solutions data. L’objectif : réduire le temps perdu sur des incidents déjà résolus mais souvent oubliés.

## 💡 Objectif

Certains problèmes sont trop spécifiques pour être bien référencés dans la documentation officielle ou sur Stack Overflow. Experia fournit un espace structuré pour conserver ces cas techniques, leurs analyses et leurs résolutions.

Exemples de questions récurrentes :

* Connexion Airbyte → Postgres local via `host.docker.internal`
* Exécution de requêtes SQL dans VSCode (extension Microsoft)
* Connexion à un replica set MongoDB local sans modifier la topologie

## 🚀 Fonctionnalités

* **Recherche full-text** sur les titres, descriptions, solutions, tags et extraits de code
* **Stockage de snippets** (commandes, configurations, scripts)
* **Gestion d’images** (screenshots encodés en base64)
* **Édition et suppression** des expériences directement dans l’interface
* **Validation Pydantic** pour garantir l’intégrité des données
* **Schema Validator MongoDB** pour formaliser la structure en base
* **Système de tags** (Docker, MongoDB, VSCode, Networking, etc.)
* **Criticité** (bloquant / non bloquant)
* **Indicateur de temps perdu** par incident
* **Authentification simple**, compatible avec les gestionnaires de mots de passe

## 🛠️ Stack technique

* **Framework** : Streamlit
* **Base de données** : MongoDB Atlas (cluster gratuit M0)
* **Validation** : Pydantic + MongoDB Schema Validator
* **Stockage médias** : encodage Base64
* **Déploiement** : Streamlit Community Cloud

## 📦 Installation locale

```bash
git clone https://github.com/ton-username/experia.git
cd experia

pip install -r requirements.txt

mkdir .streamlit
cat > .streamlit/secrets.toml << EOF
MONGO_URI = "mongodb+srv://user:pass@cluster.mongodb.net/"
APP_PASSWORD = "mot_de_passe"
EOF

streamlit run app.py
```

## 🌐 Déploiement sur Streamlit Cloud

1. Publier le code sur GitHub
2. Se rendre sur [https://share.streamlit.io](https://share.streamlit.io)
3. Connecter le dépôt
4. Renseigner les secrets nécessaires :

```toml
MONGO_URI = "mongodb+srv://user:password@cluster.mongodb.net/"
APP_PASSWORD = "mot_de_passe"
```

## 📝 Structure d’une expérience

Une expérience comporte les éléments suivants :

* **Titre** : résumé du sujet
* **Problème** : description détaillée et contexte
* **Solution** : approche validée
* **Code snippet** : configuration, commandes, scripts
* **Tags** : classification par technologie ou contexte
* **Criticité** : niveau d’impact
* **Temps perdu** : estimation du temps passé
* **Date** : résolution de l’incident

## 🎯 Exemples

**Connexion Docker → Postgres**

```
Problème : Airbyte en Docker ne détecte pas Postgres sur localhost.
Solution : Utilisation de host.docker.internal:5432.
Tags : docker, postgres, airbyte, networking
Temps perdu : 2h
```

**Raccourcis SQL sous VSCode**

```
Problème : La touche F5 n’exécute pas les requêtes SQL.
Solution : Ajout de la commande mssql.runQuery dans keybindings.json.
Tags : vscode, sql, shortcuts
Temps perdu : 30 minutes
```

## 🤝 Contribution

Le projet est open source. Les suggestions et améliorations sont les bienvenues.

## 📄 Licence

Licence MIT.