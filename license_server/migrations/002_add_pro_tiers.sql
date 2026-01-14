-- License Server Pro Database Schema
-- Add support for Pro and Enterprise tiers

-- Add tier column for license classification
ALTER TABLE licenses 
  ADD COLUMN IF NOT EXISTS tier VARCHAR(50);

-- Update existing licenses to have tier info
UPDATE licenses 
  SET tier = 'trial' 
  WHERE license_type = 'TRIAL' AND tier IS NULL;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_licenses_tier 
  ON licenses(tier);

CREATE INDEX IF NOT EXISTS idx_licenses_user_id 
  ON licenses(user_id);

-- Comments
COMMENT ON COLUMN licenses.tier IS 'License tier: trial, pro, startup, growth, enterprise';
COMMENT ON COLUMN licenses.metadata IS 'JSON metadata including capabilities for enterprise';

-- Example metadata for Enterprise:
-- {
--   "tier": "enterprise",
--   "capabilities": {
--     "max_users": 1000,
--     "offline_validation": true,
--     "sso": true,
--     "audit_logs": true,
--     "rate_limit_multiplier": 5
--   }
-- }
