SET search_path = reference_svc;

CREATE TABLE codebook (
  id VARCHAR(36) PRIMARY KEY,
  codebook_key VARCHAR(100) NOT NULL,
  codebook_name VARCHAR(255) NOT NULL,
  owning_domain VARCHAR(100) NOT NULL,
  status VARCHAR(50) NOT NULL,
  description VARCHAR(500),
  created_at TIMESTAMP NOT NULL,
  created_by VARCHAR(100) NOT NULL
);

CREATE UNIQUE INDEX ux_codebook_key ON codebook (codebook_key);

CREATE TABLE codebook_entry (
  id VARCHAR(36) PRIMARY KEY,
  codebook_id VARCHAR(36) NOT NULL,
  entry_key VARCHAR(100) NOT NULL,
  entry_value VARCHAR(255) NOT NULL,
  description VARCHAR(500),
  status VARCHAR(50) NOT NULL,
  sort_order NUMERIC(9,0),
  effective_from DATE,
  effective_to DATE,
  parent_entry_id VARCHAR(36),
  CONSTRAINT fk_codebook_entry_codebook FOREIGN KEY (codebook_id) REFERENCES codebook (id)
);

CREATE INDEX ix_codebook_entry_key ON codebook_entry (entry_key);

CREATE TABLE effective_period (
  id VARCHAR(36) PRIMARY KEY,
  codebook_id VARCHAR(36) NOT NULL,
  starts_on DATE NOT NULL,
  ends_on DATE,
  state VARCHAR(50) NOT NULL,
  approved_by VARCHAR(100),
  approved_at TIMESTAMP,
  CONSTRAINT fk_effective_period_codebook FOREIGN KEY (codebook_id) REFERENCES codebook (id)
);

CREATE TABLE reference_mapping (
  id VARCHAR(36) PRIMARY KEY,
  mapping_key VARCHAR(100) NOT NULL,
  source_domain VARCHAR(100) NOT NULL,
  source_value VARCHAR(255) NOT NULL,
  target_domain VARCHAR(100) NOT NULL,
  target_value VARCHAR(255) NOT NULL,
  effective_from DATE,
  effective_to DATE,
  mapping_status VARCHAR(50) NOT NULL
);

CREATE UNIQUE INDEX ux_reference_mapping_key ON reference_mapping (mapping_key);

CREATE TABLE audit_event (
  id VARCHAR(36) PRIMARY KEY,
  aggregate_type VARCHAR(100) NOT NULL,
  aggregate_id VARCHAR(36) NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  actor_user_id VARCHAR(100),
  actor_username VARCHAR(255),
  occurred_at TIMESTAMP NOT NULL,
  correlation_id VARCHAR(100),
  before_state VARCHAR(4000),
  after_state VARCHAR(4000),
  commentary VARCHAR(1000)
);

CREATE INDEX ix_reference_audit_aggregate ON audit_event (aggregate_type, aggregate_id);

CREATE TABLE outbox_event (
  event_id VARCHAR(36) PRIMARY KEY,
  aggregate_type VARCHAR(100) NOT NULL,
  aggregate_id VARCHAR(36) NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  occurred_at TIMESTAMP NOT NULL,
  payload VARCHAR(4000) NOT NULL,
  correlation_id VARCHAR(100),
  idempotency_key VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL,
  attempt_count NUMERIC(9,0) NOT NULL,
  available_at TIMESTAMP NOT NULL,
  last_error VARCHAR(2000)
);

CREATE INDEX ix_reference_outbox_status ON outbox_event (status, available_at);
