import sqlite3
from pathlib import Path

db_file = Path(__file__).parent.parent / "backend" / "classroom.db"
conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"Database: {db_file}")
print(f"Tables: {', '.join(tables)}")
conn.close()
