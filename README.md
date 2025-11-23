# Experia

**A knowledge management system for data engineering workflows**

Experia is a Streamlit-based application designed to document and retrieve technical solutions to common data engineering challenges. The application addresses the problem of rediscovering solutions to previously encountered technical issues that are often poorly documented or difficult to find through conventional search.

## Motivation

Data engineers frequently encounter technical challenges that are:
- Poorly documented in official sources
- Difficult to locate on Stack Overflow or similar platforms
- Environment-specific and require contextual knowledge
- Time-consuming to solve repeatedly

Examples include:
- Docker networking configurations (e.g., `host.docker.internal` for container-to-host connections)
- IDE-specific configurations and keyboard shortcuts
- Database replica set access patterns from local development environments

Experia provides a structured approach to capturing these solutions for future reference.

## Features

- **Full-text search**: Search across titles, problems, solutions, tags, and code snippets
- **Code snippet storage**: Preserve configurations, commands, and scripts with syntax highlighting
- **Screenshot support**: Attach images (PNG/JPG) encoded in base64, up to 5MB per file
- **CRUD operations**: Create, read, update, and delete experiences through the interface
- **Data validation**: Pydantic models for application-level validation and MongoDB schema validation for data integrity
- **Categorization**: Classify experiences as problems, tips, or notes
- **Tagging system**: Organize experiences with custom tags (e.g., docker, postgres, vscode)
- **Authentication**: Password-protected access with password manager compatibility

## Technology Stack

- **Frontend**: Streamlit
- **Database**: MongoDB Atlas (M0 free tier)
- **Validation**: Pydantic 2.x + MongoDB Schema Validator
- **Image Storage**: Base64-encoded binary data
- **Deployment**: Streamlit Community Cloud

## Local Installation

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- Poetry (optional) or pip

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/experia.git
cd experia

# Install dependencies
pip install -r requirements.txt

# Configure secrets
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
MONGO_URI = "mongodb+srv://user:password@cluster.mongodb.net/"
APP_PASSWORD = "your_secure_password"
EOF

# Run application
streamlit run app.py
```

## Cloud Deployment

### Streamlit Community Cloud

1. Push code to GitHub repository
2. Navigate to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository and select branch
4. Configure secrets in **Settings → Secrets**:
   ```toml
   MONGO_URI = "mongodb+srv://user:password@cluster.mongodb.net/"
   APP_PASSWORD = "your_secure_password"
   ```
5. Deploy application

## Data Schema

Each experience document contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Brief description of the issue |
| `problem` | string | Yes | Detailed problem context |
| `solution` | string | Yes | Working solution |
| `tags` | array[string] | Yes | Searchable tags |
| `category` | enum | Yes | `problème`, `astuce`, or `note` |
| `code_snippet` | string | No | Code examples or configurations |
| `notes` | string | No | Additional context |
| `screenshots` | array[object] | No | Base64-encoded images |
| `date` | string | Yes | ISO date format (YYYY-MM-DD) |

### Example Document

```json
{
  "title": "Docker container to host PostgreSQL connection",
  "problem": "Airbyte running in Docker cannot connect to PostgreSQL on host using localhost",
  "solution": "Use host.docker.internal:5432 instead of localhost:5432",
  "tags": ["docker", "postgres", "airbyte", "networking"],
  "category": "problème",
  "code_snippet": "jdbc:postgresql://host.docker.internal:5432/database",
  "notes": "Works on Mac/Windows. Linux requires 172.17.0.1 or --network host",
  "screenshots": [],
  "date": "2025-11-21"
}
```

## Data Migration

When upgrading from previous versions:

```bash
# Run migration script once
python migration.py
```

This script:
- Renames `context` → `tags`
- Converts `criticality` → `category`
- Removes deprecated `time_wasted` field
- Initializes `screenshots` array

## Development

### Requirements

```txt
streamlit>=1.51.0,<2.0.0
pymongo>=4.15.4,<5.0.0
pydantic>=2.0.0,<3.0.0
```

### MongoDB Schema Validation

The application enforces schema validation at the database level using MongoDB's `$jsonSchema` validator. This ensures data consistency even when accessing the database directly.

### Pydantic Models

Application-level validation provides immediate feedback on data entry errors before database insertion.

## Security Considerations

- Credentials stored in Streamlit secrets (never committed to version control)
- MongoDB Atlas network access configured for Streamlit Cloud IP ranges
- Dedicated database user with minimal required permissions
- Password-protected application access

## Use Cases

**Network Configuration**
```
Problem: Docker container cannot reach host services
Solution: Use host.docker.internal instead of localhost
Tags: docker, networking
```

**IDE Configuration**
```
Problem: F5 shortcut not working in VSCode SQL extension
Solution: Modify keybindings.json with mssql.runQuery command
Tags: vscode, sql, shortcuts
```

**Database Architecture**
```
Problem: MongoDB replica set access from host machine
Solution: Deploy proxy container in same Docker network
Tags: mongodb, docker, replicaset
```

## Contributing

This is a personal knowledge management tool. Feel free to fork and adapt for your own use cases.

## License

MIT License - Use freely with attribution.

---

**Built to eliminate time waste on previously solved problems.**