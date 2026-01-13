#!/usr/bin/env python3
"""Run database migration."""
import sqlite3
from pathlib import Path

migration_file = Path(__file__).parent / "migrations" / "002_lock_mode_and_enhanced_attention.sql"
db_file = Path(__file__).parent.parent / "backend" / "classroom.db"

print(f"Running migration: {migration_file.name}")
print(f"Database: {db_file}")

conn = sqlite3.connect(str(db_file))
with open(migration_file, 'r') as f:
    sql = f.read()
    # Split by semicolon and execute each statement
    for statement in sql.split(';'):
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                conn.execute(statement)
            except sqlite3.OperationalError as e:
                if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
                    print(f"  Skipping (already exists): {statement[:50]}...")
                else:
                    print(f"  Warning: {e}")

conn.commit()
conn.close()
print("✓ Migration completed successfully!")
