# migration.py
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://abguven_mongo:r!Q3yD2nWtJEr!Y@cluster0.w1esb8c.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.dev_notes

print("🔄 Migration en cours...")

# 1. Renommer context → tags (si existe)
result = db.experiences.update_many(
    {"context": {"$exists": True}},
    {"$rename": {"context": "tags"}}
)
print(f"✅ {result.modified_count} documents: context → tags")

# 2. Convertir criticality → category
# bloquant → problème
result = db.experiences.update_many(
    {"criticality": "bloquant"},
    [
        {"$set": {"category": "problème"}},
        {"$unset": "criticality"}
    ]
)
print(f"✅ {result.modified_count} documents: bloquant → problème")

# chiant → astuce
result = db.experiences.update_many(
    {"criticality": "chiant"},
    [
        {"$set": {"category": "astuce"}},
        {"$unset": "criticality"}
    ]
)
print(f"✅ {result.modified_count} documents: chiant → astuce")

# Si criticality existe encore (valeurs inconnues), mettre "note" par défaut
result = db.experiences.update_many(
    {"criticality": {"$exists": True}},
    [
        {"$set": {"category": "note"}},
        {"$unset": "criticality"}
    ]
)
if result.modified_count > 0:
    print(f"⚠️  {result.modified_count} documents avec criticality inconnue → note")

# 3. Supprimer time_wasted
result = db.experiences.update_many(
    {"time_wasted": {"$exists": True}},
    {"$unset": {"time_wasted": ""}}
)
print(f"✅ {result.modified_count} documents: suppression time_wasted")

# 4. Ajouter screenshots vide si n'existe pas
result = db.experiences.update_many(
    {"screenshots": {"$exists": False}},
    {"$set": {"screenshots": []}}
)
print(f"✅ {result.modified_count} documents: ajout screenshots[]")

print("\n🎉 Migration terminée !")
print("\n📊 Vérification:")
total = db.experiences.count_documents({})
print(f"Total documents: {total}")

for category in ["problème", "astuce", "note"]:
    count = db.experiences.count_documents({"category": category})
    print(f"  - {category}: {count}")