-- Shadow Watch Pro Database Tables
-- These tables will be used by shadowwatch-pro package
-- Free tier ignores these tables

-- ============================================================
-- CONTINUITY STATE CACHE
-- ============================================================
-- Stores cached behavioral state for Pro continuity calculation

CREATE TABLE IF NOT EXISTS continuity_state (
    subject_id VARCHAR(255) PRIMARY KEY,
    behavioral_features JSONB NOT NULL,
    variance FLOAT NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE continuity_state IS 'Cached behavioral state for Pro continuity calculation';
COMMENT ON COLUMN continuity_state.behavioral_features IS 'Compressed feature vector representing user behavior';
COMMENT ON COLUMN continuity_state.variance IS 'Historical behavioral variance (σ)';


-- ============================================================
-- DIVERGENCE HISTORY
-- ============================================================
-- Historical divergence signals for Pro trend analysis

CREATE TABLE IF NOT EXISTS divergence_history (
    id SERIAL PRIMARY KEY,
    subject_id VARCHAR(255) NOT NULL,
    magnitude FLOAT NOT NULL CHECK (magnitude >= 0.0 AND magnitude <= 1.0),
    velocity FLOAT NOT NULL,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('shock', 'creep', 'fracture', 'none')),
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE divergence_history IS 'Historical divergence signals for Pro trend analysis';
COMMENT ON COLUMN divergence_history.mode IS 'shock = fast takeover, creep = slow takeover, fracture = mixed control';


-- ============================================================
-- FEATURE SNAPSHOTS
-- ============================================================
-- Feature history for Pro variance calculation

CREATE TABLE IF NOT EXISTS feature_snapshots (
    id SERIAL PRIMARY KEY,
    subject_id VARCHAR(255) NOT NULL,
    features JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE feature_snapshots IS 'Feature history for Pro variance calculation';


-- ============================================================
-- PRE-AUTH LOGIN ATTEMPTS
-- ============================================================
-- Pre-auth events for Pro intent analysis

CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL,
    subject_id VARCHAR(255),
    success BOOLEAN NOT NULL,
    navigation_path JSONB,
    time_to_submit FLOAT,
    retry_count INT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE login_attempts IS 'Pre-auth events for Pro intent analysis';


-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_continuity_subject 
    ON continuity_state(subject_id);

CREATE INDEX IF NOT EXISTS idx_divergence_subject_time 
    ON divergence_history(subject_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_feature_snapshots_subject_time 
    ON feature_snapshots(subject_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_login_attempts_identifier 
    ON login_attempts(identifier, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_login_attempts_subject 
    ON login_attempts(subject_id, timestamp DESC);


-- ============================================================
-- RETENTION POLICIES (Optional - for production)
-- ============================================================

-- Clean up old data periodically
-- Uncomment and customize based on your retention requirements

-- DELETE FROM divergence_history WHERE timestamp < NOW() - INTERVAL '90 days';
-- DELETE FROM feature_snapshots WHERE timestamp < NOW() - INTERVAL '90 days';
-- DELETE FROM login_attempts WHERE timestamp < NOW() - INTERVAL '30 days';
