"""
Migration script: SQLite to MySQL
Migrates data from absensi.db (SQLite) to MySQL database in Laragon
"""

import sqlite3
import pymysql
import sys
from datetime import datetime

# Configuration
SQLITE_DB = 'absensi.db'
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # UPDATE THIS
    'database': 'absensi_db',
    'charset': 'utf8mb4'
}

def migrate():
    print("="*60)
    print("DATABASE MIGRATION: SQLite → MySQL")
    print("="*60)
    
    # Connect to SQLite
    print("\n[1/5] Connecting to SQLite...")
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        print("  ✓ Connected to SQLite")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        sys.exit(1)
    
    # Connect to MySQL
    print("\n[2/5] Connecting to MySQL...")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        print("  ✓ Connected to MySQL")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        print("  Make sure MySQL is running and database 'absensi_db' exists")
        sys.exit(1)
    
    # Tables to migrate (skip admin_sessions - deprecated)
    tables_to_migrate = [
        'persons',
        'embeddings', 
        'attendance_policy',
        'attendance_events',
        'daily_attendance',
        'admin_users'
    ]
    
    print("\n[3/5] Checking tables...")
    for table in tables_to_migrate:
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = sqlite_cursor.fetchone()[0]
        print(f"  {table}: {count} rows")
    
    # Migrate data
    print("\n[4/5] Migrating data...")
    total_migrated = 0
    
    for table in tables_to_migrate:
        print(f"\n  Migrating {table}...")
        
        # Get all data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"    → Empty table, skipping")
            continue
        
        # Get column info
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        # Clear existing data in MySQL (optional, comment if you want to keep)
        mysql_cursor.execute(f"DELETE FROM {table}")
        
        # Prepare insert query
        placeholders = ','.join(['%s'] * len(columns))
        column_names = ','.join([f'`{col}`' for col in columns])
        insert_query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        # Insert data
        try:
            mysql_cursor.executemany(insert_query, rows)
            mysql_conn.commit()
            print(f"    ✓ Migrated {len(rows)} rows")
            total_migrated += len(rows)
        except Exception as e:
            print(f"    ✗ Error: {e}")
            mysql_conn.rollback()
    
    # Summary
    print("\n[5/5] Migration Summary")
    print("="*60)
    print(f"Total rows migrated: {total_migrated}")
    print(f"Tables migrated: {len(tables_to_migrate)}")
    print("\nVerification:")
    
    for table in tables_to_migrate:
        mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        mysql_count = mysql_cursor.fetchone()[0]
        
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        status = "✓" if mysql_count == sqlite_count else "✗"
        print(f"  {status} {table}: SQLite={sqlite_count}, MySQL={mysql_count}")
    
    # Close connections
    sqlite_conn.close()
    mysql_conn.close()
    
    print("\n" + "="*60)
    print("✓ Migration complete!")
    print("="*60)

if __name__ == "__main__":
    try:
        migrate()
    except KeyboardInterrupt:
        print("\n\n✗ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
