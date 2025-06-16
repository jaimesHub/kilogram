# PHASE 1 SETUP SCRIPT
"""
Setup script for Phase 1: Migration + Models
Run this script to set up social authentication infrastructure
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def run_command(command, description):
    """Run shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        'DATABASE_URL',
        'MYSQL_HOST',
        'MYSQL_USER', 
        # 'MYSQL_PASSWORD',
        'MYSQL_DATABASE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "Flask-Migrate==4.0.5",
        "Authlib==1.3.0", 
        "requests==2.32.2",
        "python-dotenv==1.0.1",
        "cryptography==42.0.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    return True

def backup_database():
    """Create database backup before migration"""
    load_dotenv()
    
    db_user = os.environ.get('MYSQL_USER')
    db_password = os.environ.get('MYSQL_PASSWORD') 
    db_name = os.environ.get('MYSQL_DATABASE')
    
    if not all([db_user, db_name]):
        print("❌ Database credentials not configured")
        return False

    if not db_password:
        print("⚠️ You should set password for database connection")
    
    from datetime import datetime
    backup_file = f"backup_{db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    command = f"mysqldump -u {db_user} -p{db_password} {db_name} > {backup_file}"
    
    return run_command(command, f"Creating database backup: {backup_file}")

def initialize_flask_migrate():
    """Initialize Flask-Migrate if not already done"""
    if os.path.exists("migrations"):
        print("✅ Flask-Migrate already initialized")
        return True
    
    return run_command("flask db init", "Initializing Flask-Migrate")

def run_migration():
    """Run the social auth migration"""
    migration_file = "migrations/001_add_social_auth.sql"
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    return run_command(f"python manage_migrations.py run {migration_file}", "Running social auth migration")

def main():
    """Main setup function"""
    print("🚀 Setting up Phase 1: Migration + Models for Social Authentication")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Step 3: Backup database
    if not backup_database():
        print("⚠️  Database backup failed, but continuing...")
    
    # Step 4: Initialize Flask-Migrate
    if not initialize_flask_migrate():
        print("⚠️  Flask-Migrate initialization failed, but continuing...")
    
    # Step 5: Run migration
    if not run_migration():
        sys.exit(1)
    
    print("\n✅ Phase 1 setup completed successfully!")
    print("\nNext steps:")
    print("1. Verify database schema: python manage_migrations.py status")
    print("2. Test models in Python shell")
    print("3. Configure OAuth credentials in .env")
    print("4. Proceed to Phase 2 implementation")

if __name__ == "__main__":
    main()