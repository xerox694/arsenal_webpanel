#!/bin/bash
# Script de deploiement Arsenal V4 WebPanel

echo "Deploiement Arsenal V4 WebPanel..."

# Arreter les conteneurs existants
docker-compose down

# Construire et demarrer
docker-compose up --build -d

echo "Deploiement termine!"
echo "Panel accessible sur: http://localhost"

# Afficher les logs
docker-compose logs -f
