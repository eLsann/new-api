"""
FIXED: Migration script with table existence check
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
    'password': '',  # UPDATE THIS if you have password
    'database': 'absensi_db',
    'charset': 'utf8mb4'
}

def migrate():
    print("="*60)
    print("DATABASE MIGRATION: SQLite → MySQL (FIXED)")
    print("="*60)
    
    # Connect to SQLite
    print("\n[1/6] Connecting to SQLite...")
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        print("  ✓ Connected to SQLite")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        sys.exit(1)
    
    # Connect to MySQL
    print("\n[2/6] Connecting to MySQL...")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        print("  ✓ Connected to MySQL")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        print("  Make sure MySQL is running and database 'absensi_db' exists")
        sys.exit(1)
    
    # Check if tables exist
    print("\n[3/6] Checking MySQL tables...")
    mysql_cursor.execute("SHOW TABLES")
    existing_tables = [t[0] for t in mysql_cursor.fetchall()]
    
    if not existing_tables:
        print("  ✗ ERROR: No tables found in MySQL database!")
        print("\n  ┌─────────────────────────────────────────────┐")
        print("  │ Please create tables first:                 │")
        print("  │                                              │")
        print("  │ python -c \"from app.database import Base,  │")
        print("  │            engine; Base.metadata.create_   │")
        print("  │            all(bind=engine)\"                │")
        print("  └─────────────────────────────────────────────┘")
        mysql_conn.close()
        sqlite_conn.close()
        sys.exit(1)
    
    print(f"  ✓ Found {len(existing_tables)} tables: {', '.join(existing_tables)}")
    
    # Tables to migrate
    tables_to_migrate = [
        'persons',
        'embeddings', 
        'attendance_policy',
        'attendance_events',
        'daily_attendance',
        'admin_users'
    ]
    
    print("\n[4/6] Checking source data...")
    for table in tables_to_migrate:
        try:
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = sqlite_cursor.fetchone()[0]
            status = "✓" if table in existing_tables else "⚠"
            print(f"  {status} {table}: {count} rows")
        except:
            print(f"  ✗ {table}: not found in SQLite")
    
    # Migrate data
    print("\n[5/6] Migrating data...")
    total_migrated = 0
    
    for table in tables_to_migrate:
        print(f"\n  → {table}...")
        
        # Check if table exists in MySQL
        if table not in existing_tables:
            print(f"    ⚠ Table doesn't exist in MySQL, skipping")
            continue
        
        # Get all data from SQLite
        try:
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
        except Exception as e:
            print(f"    ✗ Error reading from SQLite: {e}")
            continue
        
        if not rows:
            print(f"    → Empty table, skipping")
            continue
        
        # Get column info
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        # Clear existing data in MySQL
        try:
            mysql_cursor.execute(f"DELETE FROM {table}")
            mysql_conn.commit()
        except Exception as e:
            print(f"    ⚠ Could not clear table: {e}")
        
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
            print(f"    ✗ Error inserting: {e}")
            mysql_conn.rollback()
    
    # Verification
    print("\n[6/6] Verification")
    print("="*60)
    
    all_ok = True
    for table in tables_to_migrate:
        if table not in existing_tables:
            continue
            
        mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        mysql_count = mysql_cursor.fetchone()[0]
        
        try:
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
        except:
            sqlite_count = 0
        
        if mysql_count == sqlite_count:
            status = "✓"
        else:
            status = "✗"
            all_ok = False
            
        print(f"  {status} {table:<20} SQLite: {sqlite_count:>4} → MySQL: {mysql_count:>4}")
    
    # Close connections
    sqlite_conn.close()
    mysql_conn.close()
    
    print("\n" + "="*60)
    if all_ok:
        print("✓ MIGRATION SUCCESSFUL!")
        print(f"Total rows migrated: {total_migrated}")
    else:
        print("⚠ MIGRATION COMPLETED WITH WARNINGS")
        print("Please check the verification results above")
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
