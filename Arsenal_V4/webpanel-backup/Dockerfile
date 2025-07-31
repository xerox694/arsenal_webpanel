# Arsenal V4 WebPanel Dockerfile
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Créer un utilisateur non-root
RUN adduser --disabled-password --gecos '' arsenal && \
    chown -R arsenal:arsenal /app
USER arsenal

# Exposer le port
EXPOSE 5000

# Variables d'environnement
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# Commande par défaut
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]
