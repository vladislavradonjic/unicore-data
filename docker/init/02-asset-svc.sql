SET search_path = asset_svc;

CREATE TABLE asset_preparation (
  id VARCHAR(36) PRIMARY KEY,
  preparation_number VARCHAR(64) NOT NULL,
  asset_type VARCHAR(50) NOT NULL,
  category_code VARCHAR(100) NOT NULL,
  supplier_code VARCHAR(100),
  acquisition_amount NUMERIC(18,2) NOT NULL,
  currency_code VARCHAR(3) NOT NULL,
  preparation_status VARCHAR(50) NOT NULL,
  source_document_id VARCHAR(36),
  description VARCHAR(500),
  created_at TIMESTAMP NOT NULL,
  created_by VARCHAR(100) NOT NULL,
  updated_at TIMESTAMP,
  updated_by VARCHAR(100)
);

CREATE UNIQUE INDEX ux_asset_preparation_number ON asset_preparation (preparation_number);

CREATE TABLE asset (
  id VARCHAR(36) PRIMARY KEY,
  asset_number VARCHAR(64) NOT NULL,
  asset_type VARCHAR(50) NOT NULL,
  category_code VARCHAR(100) NOT NULL,
  asset_name VARCHAR(255) NOT NULL,
  lifecycle_status VARCHAR(50) NOT NULL,
  activation_date DATE,
  depreciation_start_date DATE,
  currency_code VARCHAR(3) NOT NULL,
  acquisition_amount NUMERIC(18,2) NOT NULL,
  book_amount NUMERIC(18,2),
  created_at TIMESTAMP NOT NULL,
  created_by VARCHAR(100) NOT NULL,
  updated_at TIMESTAMP,
  updated_by VARCHAR(100)
);

CREATE UNIQUE INDEX ux_asset_number ON asset (asset_number);

CREATE TABLE asset_component (
  id VARCHAR(36) PRIMARY KEY,
  asset_id VARCHAR(36) NOT NULL,
  component_number VARCHAR(64) NOT NULL,
  component_name VARCHAR(255) NOT NULL,
  acquisition_amount NUMERIC(18,2) NOT NULL,
  useful_life_months NUMERIC(9,0),
  created_at TIMESTAMP NOT NULL,
  CONSTRAINT fk_asset_component_asset FOREIGN KEY (asset_id) REFERENCES asset (id)
);

CREATE TABLE asset_book_state (
  id VARCHAR(36) PRIMARY KEY,
  asset_id VARCHAR(36) NOT NULL,
  gross_amount NUMERIC(18,2) NOT NULL,
  accumulated_depreciation NUMERIC(18,2) NOT NULL,
  net_amount NUMERIC(18,2) NOT NULL,
  depreciation_rate NUMERIC(9,4),
  accounting_method VARCHAR(50),
  effective_from DATE NOT NULL,
  effective_to DATE,
  CONSTRAINT fk_asset_book_state_asset FOREIGN KEY (asset_id) REFERENCES asset (id)
);

CREATE TABLE asset_assignment (
  id VARCHAR(36) PRIMARY KEY,
  asset_id VARCHAR(36) NOT NULL,
  organization_unit_code VARCHAR(100),
  cost_center_code VARCHAR(100),
  location_code VARCHAR(100),
  accountable_person_id VARCHAR(100),
  accountable_person_name VARCHAR(255),
  effective_from DATE NOT NULL,
  effective_to DATE,
  created_at TIMESTAMP NOT NULL,
  CONSTRAINT fk_asset_assignment_asset FOREIGN KEY (asset_id) REFERENCES asset (id)
);

CREATE TABLE asset_operation_request (
  id VARCHAR(36) PRIMARY KEY,
  asset_id VARCHAR(36),
  preparation_id VARCHAR(36),
  request_number VARCHAR(64) NOT NULL,
  operation_type VARCHAR(50) NOT NULL,
  workflow_status VARCHAR(50) NOT NULL,
  requested_effective_date DATE,
  requested_payload VARCHAR(4000),
  created_at TIMESTAMP NOT NULL,
  created_by VARCHAR(100) NOT NULL,
  verified_at TIMESTAMP,
  verified_by VARCHAR(100),
  CONSTRAINT fk_asset_operation_request_asset FOREIGN KEY (asset_id) REFERENCES asset (id),
  CONSTRAINT fk_asset_operation_request_preparation FOREIGN KEY (preparation_id) REFERENCES asset_preparation (id)
);

CREATE UNIQUE INDEX ux_asset_operation_request_number ON asset_operation_request (request_number);

CREATE TABLE inventory_session (
  id VARCHAR(36) PRIMARY KEY,
  session_number VARCHAR(64) NOT NULL,
  scope_code VARCHAR(100),
  session_status VARCHAR(50) NOT NULL,
  commission_code VARCHAR(100),
  opened_at TIMESTAMP NOT NULL,
  closed_at TIMESTAMP,
  created_by VARCHAR(100) NOT NULL
);

CREATE UNIQUE INDEX ux_inventory_session_number ON inventory_session (session_number);

CREATE TABLE inventory_item_result (
  id VARCHAR(36) PRIMARY KEY,
  session_id VARCHAR(36) NOT NULL,
  asset_id VARCHAR(36),
  asset_number VARCHAR(64),
  observed_location_code VARCHAR(100),
  result_status VARCHAR(50) NOT NULL,
  observed_at TIMESTAMP NOT NULL,
  observed_by VARCHAR(100) NOT NULL,
  note VARCHAR(500),
  CONSTRAINT fk_inventory_item_session FOREIGN KEY (session_id) REFERENCES inventory_session (id),
  CONSTRAINT fk_inventory_item_asset FOREIGN KEY (asset_id) REFERENCES asset (id)
);

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

CREATE INDEX ix_asset_audit_aggregate ON audit_event (aggregate_type, aggregate_id);

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

CREATE INDEX ix_asset_outbox_status ON outbox_event (status, available_at);
