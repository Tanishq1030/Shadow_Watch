-- Shadow Watch Invariant - Database Schema
-- Phase 1: Continuity & Divergence Tables

-- =====================================================
-- Table 1: invariant_state
-- =====================================================
-- Stores per-user behavioral baseline and current state

CREATE TABLE IF NOT EXISTS invariant_state (
    user_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Baseline statistics (Welford's algorithm)
    baseline_vector JSONB NOT NULL DEFAULT '[]',  -- μ (mean vector)
    baseline_variance JSONB NOT NULL DEFAULT '[]',  -- σ² (variance vector)
    sample_count INTEGER NOT NULL DEFAULT 0,
    
    -- Continuity signals
    continuity_score REAL NOT NULL DEFAULT 1.0 CHECK (continuity_score BETWEEN 0 AND 1),
    continuity_confidence REAL NOT NULL DEFAULT 0.0 CHECK (continuity_confidence BETWEEN 0 AND 1),
    
    -- Divergence signals
    divergence_accumulated REAL NOT NULL DEFAULT 0.0 CHECK (divergence_accumulated BETWEEN 0 AND 1),
    divergence_velocity REAL NOT NULL DEFAULT 0.0,
    divergence_mode TEXT CHECK (divergence_mode IN ('shock', 'creep', 'fracture')),
    
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_invariant_state_user_id ON invariant_state(user_id);
CREATE INDEX IF NOT EXISTS idx_invariant_state_last_seen ON invariant_state(last_seen_at);

-- =====================================================
-- Table 2: continuity_history
-- =====================================================
-- Time-series log of continuity scores for analysis

CREATE TABLE IF NOT EXISTS continuity_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES invariant_state(user_id) ON DELETE CASCADE,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    continuity_score REAL NOT NULL CHECK (continuity_score BETWEEN 0 AND 1),
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    
    distance REAL NOT NULL,  -- d_t (behavioral distance)
    decay_factor REAL NOT NULL,  -- e^(-λΔt)
    
    sample_count INTEGER NOT NULL,
    
    UNIQUE(user_id, measured_at)
);

-- Indexes for time-series queries
CREATE INDEX IF NOT EXISTS idx_continuity_history_user_time 
ON continuity_history(user_id, measured_at DESC);

-- =====================================================
-- Table 3: divergence_events
-- =====================================================
-- Log critical divergence events for security review

CREATE TABLE IF NOT EXISTS divergence_events (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES invariant_state(user_id) ON DELETE CASCADE,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    mode TEXT NOT NULL CHECK (mode IN ('shock', 'creep', 'fracture')),
    magnitude REAL NOT NULL CHECK (magnitude BETWEEN 0 AND 1),
    velocity REAL NOT NULL,
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    
    -- Feature deltas for forensics
    feature_deltas JSONB,
    
    -- Resolution tracking
    resolved_at TIMESTAMPTZ,
    resolution_type TEXT CHECK (resolution_type IN ('false_positive', 'legitimate_change', 'confirmed_attack', 'user_verified')),
    notes TEXT
);

-- Indexes for security monitoring
CREATE INDEX IF NOT EXISTS idx_divergence_events_user ON divergence_events(user_id);
CREATE INDEX IF NOT EXISTS idx_divergence_events_time ON divergence_events(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_divergence_events_unresolved 
ON divergence_events(user_id, detected_at) WHERE resolved_at IS NULL;

-- =====================================================
-- Automatic timestamp updates
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_invariant_state_updated_at 
BEFORE UPDATE ON invariant_state 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Success message
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Shadow Watch Invariant tables created successfully!';
    RAISE NOTICE '  - invariant_state: User behavioral baselines';
    RAISE NOTICE '  - continuity_history: Time-series continuity log';
    RAISE NOTICE '  - divergence_events: Security event log';
END $$;
