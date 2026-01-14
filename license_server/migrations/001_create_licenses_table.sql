-- Shadow Watch License Server - Supabase Table Setup
-- Run this in Supabase SQL Editor

-- Create licenses table
CREATE TABLE IF NOT EXISTS licenses (
    id BIGSERIAL PRIMARY KEY,
    license_key TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    license_type TEXT NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    metadata JSONB DEFAULT '{}',
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index on license_key for fast lookups
CREATE INDEX IF NOT EXISTS idx_licenses_key ON licenses(license_key);

-- Create index on user_id
CREATE INDEX IF NOT EXISTS idx_licenses_user_id ON licenses(user_id);

-- Create index on license_type
CREATE INDEX IF NOT EXISTS idx_licenses_type ON licenses(license_type);

-- Create index on expires_at for expiry checks
CREATE INDEX IF NOT EXISTS idx_licenses_expires_at ON licenses(expires_at);

-- Enable Row Level Security (RLS) - IMPORTANT for Supabase
ALTER TABLE licenses ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role full access
CREATE POLICY "Service role has full access"
ON licenses
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Create policy to allow anon key to read non-revoked licenses (for validation)
CREATE POLICY "Allow public license validation"
ON licenses
FOR SELECT
TO anon
USING (is_revoked = false);

-- Grant permissions
GRANT ALL ON licenses TO service_role;
GRANT SELECT ON licenses TO anon;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Shadow Watch licenses table created successfully!';
END $$;
