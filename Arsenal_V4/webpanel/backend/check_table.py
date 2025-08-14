#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('arsenal_v4.db')
cursor = conn.cursor()

print("Structure table economy_users:")
cursor.execute('PRAGMA table_info(economy_users)')
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()
