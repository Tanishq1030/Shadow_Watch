-- Migration: 005_pre_auth_tables.sql
-- Description: Create tables for pre-authentication session tracking.

CREATE TABLE IF NOT EXISTS shadow_watch_pre_auth_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    device_fingerprint VARCHAR(128),
    signals JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    associated_user_id INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pre_auth_session_id ON shadow_watch_pre_auth_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_pre_auth_ip ON shadow_watch_pre_auth_sessions(ip_address);
CREATE INDEX IF NOT EXISTS idx_pre_auth_device ON shadow_watch_pre_auth_sessions(device_fingerprint);
CREATE INDEX IF NOT EXISTS idx_pre_auth_user ON shadow_watch_pre_auth_sessions(associated_user_id);

-- Comment for documentation
COMMENT ON TABLE shadow_watch_pre_auth_sessions IS 'Tracks anonymous behavioral signals before user authentication.';
