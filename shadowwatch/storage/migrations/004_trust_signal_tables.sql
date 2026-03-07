-- Shadow Watch - Trust Signal Tables
-- Migration 004: Device history and IP history for real trust scoring
--
-- Run after: 003_invariant_tables.sql

-- =====================================================
-- Table 1: shadow_watch_device_history
-- =====================================================
-- Known devices per user. One row per (user_id, device_fingerprint).

CREATE TABLE IF NOT EXISTS shadow_watch_device_history (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,

    -- Client-supplied device fingerprint (FingerprintJS hash or equivalent)
    device_fingerprint VARCHAR(255),
    user_agent         VARCHAR(512),

    first_seen  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    seen_count  INTEGER     NOT NULL DEFAULT 1,

    -- Computed trust level for this device (0.0-1.0)
    trust_level REAL NOT NULL DEFAULT 0.8
        CHECK (trust_level BETWEEN 0.0 AND 1.0)
);

COMMENT ON TABLE shadow_watch_device_history IS
    'Known device registry per user for device-based trust scoring.';
COMMENT ON COLUMN shadow_watch_device_history.device_fingerprint IS
    'Client-supplied hash (FingerprintJS, etc). Shadow Watch does not generate this.';
COMMENT ON COLUMN shadow_watch_device_history.trust_level IS
    '1.0=explicitly trusted, 0.8=implicitly trusted, 0.5=neutral, 0.3=flagged, 0.0=blocked';


CREATE INDEX IF NOT EXISTS idx_device_user_fingerprint
    ON shadow_watch_device_history(user_id, device_fingerprint);

CREATE INDEX IF NOT EXISTS idx_device_user_last_seen
    ON shadow_watch_device_history(user_id, last_seen DESC);


-- =====================================================
-- Table 2: shadow_watch_ip_history
-- =====================================================
-- Known IPs per user. One row per (user_id, ip_address).

CREATE TABLE IF NOT EXISTS shadow_watch_ip_history (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER     NOT NULL,

    ip_address  VARCHAR(45) NOT NULL,  -- IPv4 or IPv6
    country     CHAR(2),               -- ISO 3166-1 alpha-2 ("US", "IN", etc.)
    asn         VARCHAR(20),           -- Autonomous System Number

    first_seen  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    seen_count  INTEGER     NOT NULL DEFAULT 1,

    -- Set when user explicitly confirms a suspicious login from this IP
    is_trusted  BOOLEAN     NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE shadow_watch_ip_history IS
    'Known IP registry per user for IP-based trust scoring.';
COMMENT ON COLUMN shadow_watch_ip_history.country IS
    'ISO 3166-1 alpha-2 country code. Populated from request context or GeoIP lookup.';


CREATE INDEX IF NOT EXISTS idx_ip_user_address
    ON shadow_watch_ip_history(user_id, ip_address);

CREATE INDEX IF NOT EXISTS idx_ip_user_country
    ON shadow_watch_ip_history(user_id, country);

CREATE INDEX IF NOT EXISTS idx_ip_user_last_seen
    ON shadow_watch_ip_history(user_id, last_seen DESC);


-- =====================================================
-- Retention (optional, customize to your needs)
-- =====================================================

-- Remove very old, low-frequency device records (older than 1 year, seen only once)
-- DELETE FROM shadow_watch_device_history
-- WHERE last_seen < NOW() - INTERVAL '1 year' AND seen_count = 1;

-- Remove old, low-frequency IP records
-- DELETE FROM shadow_watch_ip_history
-- WHERE last_seen < NOW() - INTERVAL '6 months' AND seen_count = 1;


DO $$
BEGIN
    RAISE NOTICE 'Shadow Watch trust signal tables created:';
    RAISE NOTICE '  - shadow_watch_device_history';
    RAISE NOTICE '  - shadow_watch_ip_history';
END $$;
