# 🔥 Experia

**Le carnet d'expériences délirantes pour Data Engineers**

Experia est une application Streamlit qui permet de documenter et retrouver rapidement toutes ces galères techniques qui bouffent du temps et qu'on oublie 3 mois après.

## 💡 Pourquoi Experia ?

Parce que certains problèmes sont **introuvables** sur Stack Overflow :
- Comment se connecter depuis Airbyte vers Postgres local ? (`host.docker.internal`)
- Quel raccourci pour exécuter du SQL dans VSCode avec l'extension Microsoft ?
- Comment accéder à un replica set MongoDB en local sans casser la topologie ?

Ces galères méritent d'être sauvegardées pour ne **jamais** perdre de temps à nouveau.

## 🚀 Fonctionnalités

- ✅ **Recherche full-text** : Cherche dans les titres, problèmes, solutions, tags et code
- ✅ **Code snippets** : Stocke tes configurations, commandes et scripts
- ✅ **Screenshots** : Upload d'images (PNG/JPG) encodées en base64
- ✅ **Édition/Suppression** : Modifie ou supprime tes expériences directement dans l'app
- ✅ **Validation Pydantic** : Messages d'erreur clairs si données invalides
- ✅ **Schema MongoDB** : Garantit la cohérence des données en base
- ✅ **Tags contextuels** : Docker, MongoDB, VSCode, networking...
- ✅ **Criticité** : Marque les problèmes bloquants vs juste chiants
- ✅ **Temps perdu** : Track combien de temps chaque galère t'a coûté
- ✅ **Authentification** : Password-manager friendly

## 🛠️ Stack technique

- **Frontend** : Streamlit
- **Database** : MongoDB Atlas (cluster gratuit M0)
- **Validation** : Pydantic + MongoDB Schema Validator
- **Storage** : Images encodées en base64
- **Déploiement** : Streamlit Community Cloud

## 📦 Installation locale

```bash
# Clone le repo
git clone https://github.com/ton-username/experia.git
cd experia

# Installe les dépendances
pip install -r requirements.txt

# Configure MongoDB (crée .streamlit/secrets.toml)
mkdir .streamlit
cat > .streamlit/secrets.toml << EOF
MONGO_URI = "mongodb+srv://user:pass@cluster.mongodb.net/"
APP_PASSWORD = "ton_mot_de_passe"
EOF

# Lance l'app
streamlit run app.py
```

## 🌐 Déploiement sur Streamlit Cloud

1. Push ton code sur GitHub
2. Va sur [share.streamlit.io](https://share.streamlit.io)
3. Connecte ton repo
4. Dans **Settings → Secrets**, ajoute :
   ```toml
   MONGO_URI = "mongodb+srv://user:password@cluster.mongodb.net/"
   ```

## 📝 Structure des expériences

Chaque expérience contient :
- **Titre** : Description courte du problème
- **Problème** : Contexte détaillé de la galère
- **Solution** : Ce qui a finalement marché
- **Code snippet** : Commandes, config, scripts
- **Tags** : Pour retrouver facilement (docker, postgres, vscode...)
- **Criticité** : bloquant ou chiant
- **Temps perdu** : Combien de temps ça t'a coûté
- **Date** : Quand tu as résolu ça

## 🎯 Cas d'usage

**Exemple 1 : Connexion Docker → Postgres**
```
Problème : Airbyte en Docker ne trouve pas Postgres sur localhost
Solution : Utiliser host.docker.internal:5432 au lieu de localhost:5432
Tags : docker, postgres, airbyte, networking
Temps perdu : 2h
```

**Exemple 2 : Raccourcis VSCode**
```
Problème : F5 ne marche pas avec l'extension Microsoft SQL
Solution : Modifier keybindings.json avec la commande mssql.runQuery
Tags : vscode, sql, shortcuts
Temps perdu : 30min
```

## 🤝 Contribution

C'est un projet personnel mais si tu veux l'utiliser ou l'améliorer, go !

## 📄 Licence

MIT - Fais-en ce que tu veux

---

**Fait avec rage après trop de temps perdu sur des problèmes cons** 😤