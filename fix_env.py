import os

content = """# =================================
# MongoDB Atlas (Cloud Database)
# =================================
MONGODB_URL=mongodb+srv://dulcevicio:brandon20032002@oys.a9vnmf1.mongodb.net/?appName=OyS
MONGODB_DB_NAME=dulcevicio_db

# =================================
# JWT (Authentication)
# =================================
SECRET_KEY=2587461fb2443d2b43b847a77f17d1a0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43800

# =================================
# Cloudinary (Video & Image Storage)
# =================================
CLOUDINARY_CLOUD_NAME=dmxooones
CLOUDINARY_API_KEY=739168138283179
CLOUDINARY_API_SECRET=Gzn1UIqjXclRMEXJClnkrSLx11k

# =================================
# Application
# =================================
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
"""

file_path = os.path.join(os.getcwd(), '.env')
print(f"Writing clean UTF-8 .env to: {file_path}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done. File size:", os.path.getsize(file_path))
