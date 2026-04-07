SET search_path = finance_svc;

CREATE TABLE workflow_case (
  id VARCHAR(36) PRIMARY KEY,
  case_number VARCHAR(64) NOT NULL,
  aggregate_type VARCHAR(100) NOT NULL,
  aggregate_id VARCHAR(36) NOT NULL,
  operation_type VARCHAR(50) NOT NULL,
  workflow_status VARCHAR(50) NOT NULL,
  maker_user_id VARCHAR(100),
  maker_username VARCHAR(255),
  checker_user_id VARCHAR(100),
  checker_username VARCHAR(255),
  submitted_at TIMESTAMP,
  verified_at TIMESTAMP,
  returned_at TIMESTAMP,
  comment_text VARCHAR(1000),
  correlation_id VARCHAR(100)
);

CREATE UNIQUE INDEX ux_workflow_case_number ON workflow_case (case_number);

CREATE TABLE workflow_action (
  id VARCHAR(36) PRIMARY KEY,
  workflow_case_id VARCHAR(36) NOT NULL,
  action_type VARCHAR(50) NOT NULL,
  actor_user_id VARCHAR(100),
  actor_username VARCHAR(255),
  action_at TIMESTAMP NOT NULL,
  comment_text VARCHAR(1000),
  CONSTRAINT fk_workflow_action_case FOREIGN KEY (workflow_case_id) REFERENCES workflow_case (id)
);

CREATE TABLE accounting_event (
  id VARCHAR(36) PRIMARY KEY,
  event_number VARCHAR(64) NOT NULL,
  workflow_case_id VARCHAR(36),
  aggregate_type VARCHAR(100) NOT NULL,
  aggregate_id VARCHAR(36) NOT NULL,
  accounting_date DATE NOT NULL,
  currency_code VARCHAR(3) NOT NULL,
  amount NUMERIC(18,2) NOT NULL,
  event_status VARCHAR(50) NOT NULL,
  payload VARCHAR(4000),
  created_at TIMESTAMP NOT NULL,
  CONSTRAINT fk_accounting_event_case FOREIGN KEY (workflow_case_id) REFERENCES workflow_case (id)
);

CREATE UNIQUE INDEX ux_accounting_event_number ON accounting_event (event_number);

CREATE TABLE depreciation_run (
  id VARCHAR(36) PRIMARY KEY,
  run_number VARCHAR(64) NOT NULL,
  period_code VARCHAR(20) NOT NULL,
  run_status VARCHAR(50) NOT NULL,
  scheduled_at TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  initiated_by VARCHAR(100)
);

CREATE UNIQUE INDEX ux_depreciation_run_number ON depreciation_run (run_number);

CREATE TABLE depreciation_run_item (
  id VARCHAR(36) PRIMARY KEY,
  depreciation_run_id VARCHAR(36) NOT NULL,
  asset_id VARCHAR(36),
  asset_number VARCHAR(64),
  amount NUMERIC(18,2) NOT NULL,
  status VARCHAR(50) NOT NULL,
  note VARCHAR(500),
  CONSTRAINT fk_depreciation_run_item_run FOREIGN KEY (depreciation_run_id) REFERENCES depreciation_run (id)
);

CREATE TABLE period_calendar (
  id VARCHAR(36) PRIMARY KEY,
  period_code VARCHAR(20) NOT NULL,
  fiscal_year NUMERIC(4,0) NOT NULL,
  fiscal_period NUMERIC(2,0) NOT NULL,
  starts_on DATE NOT NULL,
  ends_on DATE NOT NULL,
  locked_flag VARCHAR(5) NOT NULL,
  lock_reason VARCHAR(255)
);

CREATE UNIQUE INDEX ux_period_calendar_period_code ON period_calendar (period_code);

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

CREATE INDEX ix_finance_audit_aggregate ON audit_event (aggregate_type, aggregate_id);

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

CREATE INDEX ix_finance_outbox_status ON outbox_event (status, available_at);
