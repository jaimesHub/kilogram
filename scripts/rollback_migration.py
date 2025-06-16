import os
import sys
import mysql.connector
from dotenv import load_dotenv

def rollback_social_auth_migration():
    """Rollback the social authentication migration"""
    
    load_dotenv()
    
    db_config = {
        'host': os.environ.get('MYSQL_HOST'),
        'user': os.environ.get('MYSQL_USER'),
        'password': os.environ.get('MYSQL_PASSWORD'),
        'database': os.environ.get('MYSQL_DATABASE')
    }
    
    rollback_sql = [
        "DROP INDEX IF EXISTS idx_users_signup_method ON users",
        "DROP INDEX IF EXISTS idx_social_accounts_user_id ON social_accounts",
        "DROP INDEX IF EXISTS idx_social_accounts_provider_lookup ON social_accounts", 
        "DROP INDEX IF EXISTS idx_social_accounts_user_provider ON social_accounts",
        "DROP TABLE IF EXISTS social_accounts",
        "ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NOT NULL",
        "ALTER TABLE users DROP COLUMN IF EXISTS signup_method",
        "DELETE FROM schema_migrations WHERE version = '001_add_social_auth.sql'"
    ]
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("🔄 Rolling back social authentication migration...")
        
        for sql in rollback_sql:
            try:
                cursor.execute(sql)
                print(f"✅ Executed: {sql}")
            except mysql.connector.Error as e:
                print(f"⚠️  Warning (continuing): {sql} - {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Rollback completed successfully!")
        print("You can now re-run: python manage_migrations.py run migrations/001_add_social_auth.sql")
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    rollback_social_auth_migration()