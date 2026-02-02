#!/bin/bash

# Render startup script for Core Integrator Sprint
echo "Starting Core Integrator Sprint deployment..."

# Create data directories
mkdir -p data
mkdir -p logs/bridge

# Initialize SQLite database
python -c "
import sqlite3
import os
from pathlib import Path

# Ensure data directory exists
Path('data').mkdir(exist_ok=True)

# Initialize main database
db_path = 'data/context.db'
with sqlite3.connect(db_path) as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            module TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            request_data TEXT NOT NULL,
            response_data TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            generation_id TEXT PRIMARY KEY,
            user_id TEXT,
            interaction_id INTEGER,
            created_at TEXT,
            payload TEXT
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_module_timestamp 
        ON interactions(user_id, module, timestamp DESC)
    ''')

# Initialize nonce database
nonce_db_path = 'data/nonce_store.db'
with sqlite3.connect(nonce_db_path) as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS nonces (
            nonce TEXT PRIMARY KEY,
            timestamp INTEGER NOT NULL,
            user_id TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp ON nonces(timestamp)
    ''')

print('Database initialization complete')
"

# Start the application
echo "Starting FastAPI application..."
exec python main.py