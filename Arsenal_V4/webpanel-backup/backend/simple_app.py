#!/usr/bin/env python3
# Test simple
from flask import Flask
from flask_socketio import SocketIO

print("🔧 Création d'une version simplifiée...")

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/api/test')
def test():
    return {'status': 'ok'}

print(f"✅ Variables définies: app={type(app)}, socketio={type(socketio)}")

# Exporter pour usage externe
__all__ = ['app', 'socketio']
