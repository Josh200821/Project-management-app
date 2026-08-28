-- PostgreSQL initialization for local development
-- Extensions are created in Alembic migration 001
-- This file is run by Docker on first container start

CREATE DATABASE saasplatform;
\c saasplatform

-- Create app role with restricted permissions
DO $$BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_role') THEN
    CREATE ROLE app_role;
  END IF;
END$$;

-- Immutable audit log enforcement (run after migrations)
-- REVOKE UPDATE, DELETE ON audit_logs FROM app_role;
