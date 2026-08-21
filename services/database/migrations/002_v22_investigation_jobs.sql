CREATE TABLE IF NOT EXISTS scraper_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL,
  url TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'QUEUED',
  attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 3,
  error_message TEXT,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scraper_jobs_queue ON scraper_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS idx_scraper_jobs_case ON scraper_jobs(case_id, created_at DESC);

ALTER TABLE evidence ADD COLUMN IF NOT EXISTS extraction_method TEXT;
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS provenance JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE evidence ADD COLUMN IF NOT EXISTS independent_source_key TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS uq_evidence_content_per_case
  ON evidence(case_id, source_url, content_hash)
  WHERE content_hash IS NOT NULL;
