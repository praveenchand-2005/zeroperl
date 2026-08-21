CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  display_name TEXT NOT NULL,
  role TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, email)
);

CREATE TABLE IF NOT EXISTS cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  case_number TEXT NOT NULL,
  lender_name TEXT,
  loan_reference_masked TEXT,
  borrower_name TEXT NOT NULL,
  dpd INTEGER,
  outstanding_amount NUMERIC(18,2),
  priority TEXT NOT NULL DEFAULT 'MEDIUM',
  status TEXT NOT NULL DEFAULT 'OPEN',
  assigned_user_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, case_number)
);

CREATE TABLE IF NOT EXISTS investigations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  requested_by UUID REFERENCES users(id),
  depth TEXT NOT NULL DEFAULT 'STANDARD',
  status TEXT NOT NULL DEFAULT 'QUEUED',
  identity_score NUMERIC(5,2),
  address_score NUMERIC(5,2),
  contact_score NUMERIC(5,2),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS source_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_type TEXT NOT NULL,
  base_url TEXT,
  jurisdiction TEXT,
  access_method TEXT NOT NULL DEFAULT 'HTTP',
  authorization_required BOOLEAN NOT NULL DEFAULT TRUE,
  public_access_allowed BOOLEAN NOT NULL DEFAULT FALSE,
  allowed_domains JSONB NOT NULL DEFAULT '[]'::jsonb,
  allowed_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
  rate_limit_per_minute INTEGER NOT NULL DEFAULT 30,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  terms_reference TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, source_id)
);

CREATE TABLE IF NOT EXISTS scraper_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
  source_registry_id UUID REFERENCES source_registry(id),
  job_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'QUEUED',
  priority TEXT NOT NULL DEFAULT 'NORMAL',
  requested_url TEXT,
  requested_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
  result_count INTEGER NOT NULL DEFAULT 0,
  error_code TEXT,
  error_message TEXT,
  attempts INTEGER NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS addresses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  raw_address TEXT NOT NULL,
  normalized_address TEXT,
  city TEXT,
  district TEXT,
  state TEXT,
  postal_code TEXT,
  country TEXT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  verification_status TEXT NOT NULL DEFAULT 'UNVERIFIED',
  confidence NUMERIC(5,2),
  first_seen TIMESTAMPTZ,
  last_seen TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
  investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
  scraper_job_id UUID REFERENCES scraper_jobs(id) ON DELETE SET NULL,
  source_name TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_reference TEXT,
  source_url TEXT,
  entity_type TEXT,
  field_name TEXT,
  raw_value TEXT,
  normalized_value TEXT,
  observed_at TIMESTAMPTZ,
  retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  verification_status TEXT NOT NULL DEFAULT 'UNVERIFIED',
  confidence NUMERIC(5,2),
  content_hash TEXT,
  extraction_method TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  case_id UUID REFERENCES cases(id),
  action TEXT NOT NULL,
  reason TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cases_org_status ON cases(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_investigations_case ON investigations(case_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_source_registry_org ON source_registry(organization_id, enabled);
CREATE INDEX IF NOT EXISTS idx_scraper_jobs_investigation ON scraper_jobs(investigation_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence(case_id, retrieved_at DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_investigation ON evidence(investigation_id, retrieved_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_case ON audit_logs(case_id, created_at DESC);
