-- Deliverable D7 PostgreSQL DDL Schema Migration Script
-- Extends the decision_records table with provenance and reasoning trail data.
-- Adds the calibration_metrics table to store historical judge calibration data.

INSERT INTO scof.schema_version (version, description)
VALUES ('3.0.0', 'D7 Observability & Explainability schema extensions')
ON CONFLICT (version) DO NOTHING;

-- 1. Extend Decision Records Table (Idempotent)
ALTER TABLE scof.decision_records 
ADD COLUMN IF NOT EXISTS consensus_bundle_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS source_bundle_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS trace_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS wcs NUMERIC(5,4),
ADD COLUMN IF NOT EXISTS escalation_tier VARCHAR(50),
ADD COLUMN IF NOT EXISTS decision_method VARCHAR(50),
ADD COLUMN IF NOT EXISTS reasoning_trail JSONB,
ADD COLUMN IF NOT EXISTS meeting_log_entries JSONB;

-- 2. Calibration Metrics Table
CREATE TABLE IF NOT EXISTS scof.calibration_metrics (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    recommendation_kappa NUMERIC(5,4),
    escalation_tier_kappa NUMERIC(5,4),
    sample_size INT,
    pass_status BOOLEAN,
    report_data JSONB NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_decision_records_trace ON scof.decision_records(trace_id);
CREATE INDEX IF NOT EXISTS idx_decision_records_source_bundle ON scof.decision_records(source_bundle_id);
CREATE INDEX IF NOT EXISTS idx_calibration_metrics_timestamp ON scof.calibration_metrics(timestamp);
