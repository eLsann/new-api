"""
Migration script that uses SQLAlchemy connection (same as the app)
This ensures we use the correct database from .env
"""
import sys
import os
import sqlite3

# Add grandparent directory to path (newApi root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import app's database connection
from app.database import SessionLocal, engine
from sqlalchemy import text

SQLITE_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'absensi.db')

def migrate():
    print("="*60)
    print("DATABASE MIGRATION: SQLite → MySQL (via SQLAlchemy)")
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
    
    # Get SQLAlchemy session (uses .env config)
    print("\n[2/5] Connecting to MySQL via SQLAlchemy...")
    try:
        # Print the URL being used
        print(f"  → Configured Database URL: {engine.url}")
        
        if 'sqlite' in str(engine.url):
            print("  ⚠ WARNING: SQLAlchemy is using SQLite! Check your .env configuration.")
            print("    It should be: mysql+pymysql://...")
        
        db = SessionLocal()
        # Test connection
        db.execute(text("SELECT 1"))
        print("  ✓ Connected to MySQL")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        sys.exit(1)
    
    # Check tables exist
    print("\n[3/5] Checking MySQL tables...")
    result = db.execute(text("SHOW TABLES"))
    tables_in_db = [row[0] for row in result.fetchall()]
    print(f"  ✓ Found tables: {', '.join(tables_in_db)}")
    
    if not tables_in_db:
        print("  ✗ No tables found! Run this first:")
        print('  python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"')
        sys.exit(1)
    
    # Tables to migrate
    tables = ['persons', 'embeddings', 'attendance_policy', 
              'attendance_events', 'daily_attendance', 'admin_users']
    
    print("\n[4/5] Migrating data...")
    total = 0
    
    for table in tables:
        print(f"\n  → {table}...")
        
        # Check if table exists in MySQL
        if table not in tables_in_db:
            print(f"    ⚠ Skipping - table not in MySQL")
            continue
        
        # Get data from SQLite
        try:
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
        except:
            print(f"    ⚠ Skipping - table not in SQLite")
            continue
        
        if not rows:
            print(f"    → Empty table")
            continue
        
        # Get columns
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        # Clear existing data
        try:
            db.execute(text(f"DELETE FROM `{table}`"))
            db.commit()
        except Exception as e:
            print(f"    ⚠ Clear failed: {e}")
            db.rollback()
        
        # Insert data row by row
        success = 0
        for row in rows:
            try:
                cols = ', '.join([f'`{c}`' for c in columns])
                placeholders = ', '.join([':p' + str(i) for i in range(len(columns))])
                params = {f'p{i}': val for i, val in enumerate(row)}
                
                db.execute(text(f"INSERT INTO `{table}` ({cols}) VALUES ({placeholders})"), params)
                success += 1
            except Exception as e:
                print(f"    ⚠ Row error: {e}")
        
        db.commit()
        print(f"    ✓ Migrated {success}/{len(rows)} rows")
        total += success
    
    # Summary
    print("\n[5/5] Verification...")
    print("="*60)
    
    for table in tables:
        if table not in tables_in_db:
            continue
        
        # MySQL count
        result = db.execute(text(f"SELECT COUNT(*) FROM `{table}`"))
        mysql_count = result.fetchone()[0]
        
        # SQLite count
        try:
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
        except:
            sqlite_count = 0
        
        status = "✓" if mysql_count == sqlite_count else "⚠"
        print(f"  {status} {table:<20} SQLite: {sqlite_count:>4} → MySQL: {mysql_count:>4}")
    
    db.close()
    sqlite_conn.close()
    
    print("\n" + "="*60)
    print(f"✓ Migration complete! Total rows: {total}")
    print("="*60)

if __name__ == "__main__":
    migrate()
