import sqlite3
import os

db_path = 'absensi.db'

if not os.path.exists(db_path):
    print(f"Database {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("DATABASE ANALYSIS: absensi.db")
print("=" * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nFound {len(tables)} tables:\n")

for table in tables:
    table_name = table[0]
    print(f"\n{'='*60}")
    print(f"TABLE: {table_name}")
    print(f"{'='*60}")
    
    # Get schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("\nSchema:")
    print(f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'Default':<15} {'PK'}")
    print("-" * 75)
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        nullable = "NOT NULL" if notnull else "NULL"
        default_val = str(default) if default else ""
        pk_mark = "PK" if pk else ""
        print(f"{name:<20} {type_:<15} {nullable:<10} {default_val:<15} {pk_mark}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nRow count: {count}")
    
    # Show sample data if exists
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print(f"\nSample data (first 3 rows):")
        col_names = [col[1] for col in columns]
        print(" | ".join(col_names))
        print("-" * 75)
        for row in rows:
            print(" | ".join(str(val)[:30] if val else "NULL" for val in row))

# Database file size
db_size = os.path.getsize(db_path)
print(f"\n{'='*60}")
print(f"Database file size: {db_size:,} bytes ({db_size/1024:.2f} KB)")
print(f"{'='*60}")

conn.close()
print("\n✓ Analysis complete!")
