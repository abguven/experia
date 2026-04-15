# Experia

Personal knowledge base for storing and retrieving technical experiences encountered during data engineering work. The goal: stop losing time on problems you already solved.

## Features

- **Full-text search** across titles, problems, solutions, tags, and code snippets
- **Google OAuth2 authentication** with email whitelist
- **3 categories** — problem, tip, note
- **Tag system** for technology-based classification
- **Code snippets** with syntax highlighting
- **Screenshot upload** (PNG/JPG, max 5MB, stored as base64)
- **Pydantic validation** + MongoDB schema validator for data integrity

## Tech stack

| Layer      | Technology                            |
| ---------- | ------------------------------------- |
| Framework  | Streamlit                             |
| Database   | MongoDB Atlas (M0 free tier)          |
| Validation | Pydantic v1 + MongoDB Schema Validator|
| Auth       | Streamlit native Google OAuth2        |
| Media      | Base64 encoding                       |
| Deployment | Streamlit Community Cloud             |

## Local setup

```bash
git clone https://github.com/abguven/experia.git
cd experia
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` :

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-random-secret"
authorized_emails = ["your-email@gmail.com"]

[auth.google]
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[mongo]
uri = "mongodb+srv://user:password@cluster.mongodb.net/?appName=Cluster0"
```

```bash
streamlit run app.py
```

## Streamlit Cloud deployment

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect the repo
3. In **App settings → Secrets**, paste your `secrets.toml` content with:
   - `redirect_uri` set to `https://your-app.streamlit.app/oauth2callback`
4. Add `https://your-app.streamlit.app/oauth2callback` to authorized redirect URIs in Google Cloud Console

## Experience structure

| Field          | Required | Description                               |
| -------------- | -------- | ----------------------------------------- |
| `title`        | Yes      | Short summary                             |
| `problem`      | Yes      | Problem description and context           |
| `solution`     | Yes      | Validated fix or approach                 |
| `tags`         | Yes      | At least one tag (docker, postgres, etc.) |
| `category`     | Yes      | `problème`, `astuce`, or `note`           |
| `code_snippet` | No       | Commands, configs, scripts                |
| `notes`        | No       | Additional context                        |
| `screenshots`  | No       | PNG/JPG up to 5MB each                    |
| `date`         | Auto     | Set on creation                           |

## License

MIT
