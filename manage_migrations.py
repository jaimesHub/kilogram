import os
import sys
from datetime import datetime
import mysql.connector

class MigrationManager:
    def __init__(self):
        self.db_config = {
            'host': os.environ.get('MYSQL_HOST'),
            'user': os.environ.get('MYSQL_USER'),
            'password': os.environ.get('MYSQL_PASSWORD'),
            'database': os.environ.get('MYSQL_DATABASE')
        }
        self.migrations_dir = "migrations"
        self.ensure_migrations_table()
    
    def ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Migration tracking table ready")
            
        except mysql.connector.Error as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def run_migration(self, migration_file):
        """Run a specific migration file"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Read migration file
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Extract SQL statements (ignore comments and rollback section)
            lines = sql_content.split('\n')
            sql_statements = []
            in_rollback = False
            current_statement = ""
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if line.startswith('--') or line.startswith('"""') or not line:
                    continue
                
                # Stop at rollback section
                if 'ROLLBACK SQL' in line:
                    break
                
                current_statement += line + " "
                
                # Execute when we hit a semicolon
                if line.endswith(';'):
                    if current_statement.strip():
                        sql_statements.append(current_statement.strip())
                    current_statement = ""
            
            # Execute all statements
            for statement in sql_statements:
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                        print(f"✅ Executed: {statement[:50]}...")
                    except mysql.connector.Error as e:
                        print(f"❌ Failed to execute: {statement[:50]}...")
                        print(f"   Error: {e}")
                        raise
            
            # Mark migration as applied
            migration_name = os.path.basename(migration_file)
            cursor.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (migration_name,)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Migration completed: {migration_name}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            sys.exit(1)
    
    def check_migration_status(self):
        """Check which migrations have been applied"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
            applied = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            print("📋 Migration Status:")
            print(f"Applied migrations: {len(applied)}")
            for migration in applied:
                print(f"  ✅ {migration}")
            
            return applied
            
        except mysql.connector.Error as e:
            print(f"❌ Failed to check migration status: {e}")
            return []

if __name__ == "__main__":
    manager = MigrationManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            manager.check_migration_status()
        elif sys.argv[1] == "run" and len(sys.argv) > 2:
            migration_file = sys.argv[2]
            if os.path.exists(migration_file):
                manager.run_migration(migration_file)
            else:
                print(f"❌ Migration file not found: {migration_file}")
    else:
        print("Usage:")
        print("  python manage_migrations.py status")
        print("  python manage_migrations.py run <migration_file>")