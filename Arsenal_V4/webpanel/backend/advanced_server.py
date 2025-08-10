#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🚀 Démarrage du serveur Arsenal_V4 Advanced...")

# Minimal version for Gunicorn deployment
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Arsenal V4 WebPanel - Render Deployment Test"

@app.route('/health')
def health():
    return {"status": "healthy", "service": "Arsenal_V4_WebPanel"}

# Fichier prêt pour Gunicorn deployment
