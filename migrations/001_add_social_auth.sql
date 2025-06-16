-- Migration: Add social authentication support
-- Created: 2025-06-16
-- Version: 001_add_social_auth

-- Add signup_method column to users table
ALTER TABLE users ADD COLUMN signup_method VARCHAR(20) DEFAULT 'username';

-- Update existing users (current users login with username/password)
UPDATE users SET signup_method = 'username' WHERE signup_method IS NULL;

-- Make password_hash nullable for social-only users
ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NULL;

-- Create social_accounts table
CREATE TABLE social_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(100),
    access_token TEXT,
    refresh_token TEXT,
    expires_at INT,
    profile_data JSON,
    created_at INT NOT NULL,
    updated_at INT NOT NULL,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_social_accounts_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique Constraints  
    CONSTRAINT unique_provider_account 
        UNIQUE (provider, provider_id)
);

-- Create indexes for performance
CREATE INDEX idx_social_accounts_user_provider ON social_accounts(user_id, provider);
CREATE INDEX idx_social_accounts_provider_lookup ON social_accounts(provider, provider_id);
CREATE INDEX idx_social_accounts_user_id ON social_accounts(user_id);
CREATE INDEX idx_users_signup_method ON users(signup_method);

-- ROLLBACK SQL (for manual rollback if needed):
-- DROP INDEX idx_users_signup_method ON users;
-- DROP INDEX idx_social_accounts_user_id ON social_accounts;
-- DROP INDEX idx_social_accounts_provider_lookup ON social_accounts;
-- DROP INDEX idx_social_accounts_user_provider ON social_accounts;
-- DROP TABLE social_accounts;
-- ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NOT NULL;
-- ALTER TABLE users DROP COLUMN signup_method;
