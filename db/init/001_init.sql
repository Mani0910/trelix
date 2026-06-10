CREATE TABLE IF NOT EXISTS app_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(120) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deployment_runs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES app_users(id),
    vm_type VARCHAR(32) NOT NULL,
    source_file VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS server_inventory (
    id BIGSERIAL PRIMARY KEY,
    ip_address INET NOT NULL,
    vm_type VARCHAR(32) NOT NULL,
    putty_username VARCHAR(120),
    putty_password_encrypted TEXT,
    previous_putty_password TEXT,
    root_password_encrypted TEXT,
    previous_root_password TEXT,
    credential_valid BOOLEAN,
    created_by BIGINT REFERENCES app_users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_credential_update TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (ip_address, vm_type)
);

CREATE TABLE IF NOT EXISTS deployment_results (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES deployment_runs(id) ON DELETE CASCADE,
    server_id BIGINT NOT NULL REFERENCES server_inventory(id) ON DELETE CASCADE,
    trelix_installed BOOLEAN NOT NULL DEFAULT FALSE,
    trelix_version VARCHAR(128),
    credential_valid BOOLEAN,
    status VARCHAR(32) NOT NULL,
    message TEXT,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_server_inventory_ip ON server_inventory (ip_address);
CREATE INDEX IF NOT EXISTS idx_server_inventory_vm_type ON server_inventory (vm_type);
CREATE INDEX IF NOT EXISTS idx_deployment_results_status ON deployment_results (status);
CREATE INDEX IF NOT EXISTS idx_deployment_results_checked_at ON deployment_results (checked_at);
CREATE UNIQUE INDEX IF NOT EXISTS uq_deployment_results_server_id ON deployment_results (server_id);
