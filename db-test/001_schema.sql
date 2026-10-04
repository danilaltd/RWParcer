-- PostgreSQL schema for the transport monitoring application.
-- Target: PostgreSQL 15+
-- No ORM assumptions.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS identity;
CREATE SCHEMA IF NOT EXISTS transport;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS messaging;
CREATE SCHEMA IF NOT EXISTS bot;
CREATE SCHEMA IF NOT EXISTS audit;

-- -----------------------------------------------------------------------------
-- Generic updated_at trigger
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- -----------------------------------------------------------------------------
-- Identity
-- -----------------------------------------------------------------------------

CREATE TABLE identity.users (
    id                                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id                    bigint NOT NULL UNIQUE,
    telegram_chat_id                    bigint NOT NULL,
    username                            text,
    display_name                        text,
    status                              text NOT NULL DEFAULT 'ACTIVE',
    max_subscriptions                   integer NOT NULL DEFAULT 5,
    min_subscription_interval_seconds   integer NOT NULL DEFAULT 15,
    created_at                          timestamptz NOT NULL DEFAULT now(),
    updated_at                          timestamptz NOT NULL DEFAULT now(),
    last_activity_at                    timestamptz,

    CONSTRAINT users_status_chk
        CHECK (status IN ('ACTIVE', 'BLOCKED')),
    CONSTRAINT users_max_subscriptions_chk
        CHECK (max_subscriptions > 0),
    CONSTRAINT users_min_subscription_interval_chk
        CHECK (min_subscription_interval_seconds > 0)
);

CREATE INDEX users_status_idx ON identity.users (status);
CREATE INDEX users_last_activity_idx ON identity.users (last_activity_at);

CREATE TABLE identity.roles (
    id      smallint PRIMARY KEY,
    code    text NOT NULL UNIQUE,
    name    text NOT NULL
);

CREATE TABLE identity.user_roles (
    user_id             uuid NOT NULL,
    role_id             smallint NOT NULL,
    assigned_at         timestamptz NOT NULL DEFAULT now(),
    assigned_by_user_id uuid,

    PRIMARY KEY (user_id, role_id),

    CONSTRAINT user_roles_user_fk
        FOREIGN KEY (user_id)
        REFERENCES identity.users (id)
        ON DELETE CASCADE,

    CONSTRAINT user_roles_role_fk
        FOREIGN KEY (role_id)
        REFERENCES identity.roles (id)
        ON DELETE RESTRICT,

    CONSTRAINT user_roles_assigned_by_fk
        FOREIGN KEY (assigned_by_user_id)
        REFERENCES identity.users (id)
        ON DELETE SET NULL
);

CREATE INDEX user_roles_role_idx ON identity.user_roles (role_id);

CREATE TRIGGER users_set_updated_at
BEFORE UPDATE ON identity.users
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- -----------------------------------------------------------------------------
-- Transport
-- -----------------------------------------------------------------------------

CREATE TABLE transport.providers (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code            text NOT NULL UNIQUE,
    name            text NOT NULL,
    adapter_code    text NOT NULL UNIQUE,
    base_url        text,
    is_active       boolean NOT NULL DEFAULT true,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT providers_code_chk
        CHECK (length(trim(code)) > 0),
    CONSTRAINT providers_adapter_code_chk
        CHECK (length(trim(adapter_code)) > 0)
);

CREATE INDEX providers_active_idx ON transport.providers (is_active);

CREATE TABLE transport.stops (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id     uuid NOT NULL,
    external_code   text NOT NULL,
    name            text NOT NULL,
    latitude        numeric(9,6),
    longitude       numeric(9,6),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT stops_provider_fk
        FOREIGN KEY (provider_id)
        REFERENCES transport.providers (id)
        ON DELETE RESTRICT,

    CONSTRAINT stops_coordinates_chk
        CHECK (
            (latitude IS NULL AND longitude IS NULL)
            OR
            (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
        ),
    CONSTRAINT stops_name_chk
        CHECK (length(trim(name)) > 0)
);

CREATE UNIQUE INDEX stops_provider_external_code_uq
    ON transport.stops (provider_id, external_code);
CREATE INDEX stops_provider_name_idx
    ON transport.stops (provider_id, name);

CREATE TABLE transport.routes (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    from_stop_id    uuid NOT NULL,
    to_stop_id      uuid NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT routes_from_stop_fk
        FOREIGN KEY (from_stop_id)
        REFERENCES transport.stops (id)
        ON DELETE RESTRICT,

    CONSTRAINT routes_to_stop_fk
        FOREIGN KEY (to_stop_id)
        REFERENCES transport.stops (id)
        ON DELETE RESTRICT,

    CONSTRAINT routes_different_stops_chk
        CHECK (from_stop_id <> to_stop_id)
);

CREATE UNIQUE INDEX routes_from_to_uq
    ON transport.routes (from_stop_id, to_stop_id);

CREATE TABLE transport.services (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id     uuid NOT NULL,
    route_id        uuid NOT NULL,
    transport_mode  text NOT NULL,
    external_number text NOT NULL,
    service_type    text,
    days_rule           text,
    days_exceptions     text,
    valid_from          date,
    valid_to            date,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT services_provider_fk
        FOREIGN KEY (provider_id)
        REFERENCES transport.providers (id)
        ON DELETE RESTRICT,

    CONSTRAINT services_route_fk
        FOREIGN KEY (route_id)
        REFERENCES transport.routes (id)
        ON DELETE RESTRICT,

    CONSTRAINT services_transport_mode_chk
        CHECK (length(trim(transport_mode)) > 0),
    CONSTRAINT services_external_number_chk
        CHECK (length(trim(external_number)) > 0),
    CONSTRAINT service_routes_validity_chk
        CHECK (valid_from IS NULL OR valid_to IS NULL OR valid_to >= valid_from)
);

CREATE UNIQUE INDEX services_provider_mode_number_route_uq
    ON transport.services (provider_id, transport_mode, external_number, route_id);
CREATE INDEX services_provider_mode_idx
    ON transport.services (provider_id, transport_mode);
CREATE INDEX services_route_idx
    ON transport.services (route_id);

CREATE TABLE transport.service_routes (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id          uuid NOT NULL,
    route_id            uuid NOT NULL,
    departure_time      time NOT NULL,
    arrival_time        time NOT NULL,
    duration_minutes    integer NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT service_routes_service_fk
        FOREIGN KEY (service_id)
        REFERENCES transport.services (id)
        ON DELETE RESTRICT,

    CONSTRAINT service_routes_route_fk
        FOREIGN KEY (route_id)
        REFERENCES transport.routes (id)
        ON DELETE RESTRICT,

    CONSTRAINT service_routes_duration_chk
        CHECK (duration_minutes > 0)
);

CREATE UNIQUE INDEX service_routes_business_uq
    ON transport.service_routes (service_id, route_id);
CREATE INDEX service_routes_service_idx
    ON transport.service_routes (service_id);
CREATE INDEX service_routes_route_idx
    ON transport.service_routes (route_id);

CREATE TRIGGER providers_set_updated_at
BEFORE UPDATE ON transport.providers
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER stops_set_updated_at
BEFORE UPDATE ON transport.stops
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER routes_set_updated_at
BEFORE UPDATE ON transport.routes
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER services_set_updated_at
BEFORE UPDATE ON transport.services
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER service_routes_set_updated_at
BEFORE UPDATE ON transport.service_routes
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- -----------------------------------------------------------------------------
-- Monitoring
-- -----------------------------------------------------------------------------

CREATE TABLE monitoring.subscriptions (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             uuid NOT NULL,
    service_route_id    uuid NOT NULL,
    target_date         date NOT NULL,
    status              text NOT NULL DEFAULT 'ACTIVE',
    last_checked_at     timestamptz,
    next_check_at       timestamptz,
    last_notified_at    timestamptz,
    created_at          timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT subscriptions_user_fk
        FOREIGN KEY (user_id)
        REFERENCES identity.users (id)
        ON DELETE CASCADE,

    CONSTRAINT subscriptions_service_route_fk
        FOREIGN KEY (service_route_id)
        REFERENCES transport.service_routes (id)
        ON DELETE RESTRICT,

    CONSTRAINT subscriptions_status_chk
        CHECK (status IN ('ACTIVE', 'PAUSED', 'CANCELLED'))

    -- TODO: Add constraint to ensure that next_check_at is always greater than last_checked_at, if both are not null. 
    -- TODO: Add constraint to ensure that next_check_at not null only if status is 'ACTIVE' or 'PAUSED'. 
);

CREATE UNIQUE INDEX subscriptions_active_paused_uq
    ON monitoring.subscriptions (user_id, service_route_id, target_date)
    WHERE status IN ('ACTIVE', 'PAUSED');

CREATE INDEX subscriptions_user_idx
    ON monitoring.subscriptions (user_id);
CREATE INDEX subscriptions_due_idx
    ON monitoring.subscriptions (next_check_at, id)
    WHERE status = 'ACTIVE';

CREATE TABLE monitoring.favorites (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             uuid NOT NULL,
    service_route_id    uuid NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT favorites_user_fk
        FOREIGN KEY (user_id)
        REFERENCES identity.users (id)
        ON DELETE CASCADE,

    CONSTRAINT favorites_service_route_fk
        FOREIGN KEY (service_route_id)
        REFERENCES transport.service_routes (id)
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX favorites_user_route_uq
    ON monitoring.favorites (user_id, service_route_id);
CREATE INDEX favorites_user_idx ON monitoring.favorites (user_id);

CREATE TABLE monitoring.availability_snapshots (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id     uuid NOT NULL,
    checked_at          timestamptz NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT availability_snapshots_subscription_fk
        FOREIGN KEY (subscription_id)
        REFERENCES monitoring.subscriptions (id)
        ON DELETE CASCADE
);

CREATE INDEX availability_snapshots_subscription_idx
    ON monitoring.availability_snapshots (subscription_id, checked_at DESC);

CREATE TABLE monitoring.availability_snapshot_seats (
    snapshot_id     uuid NOT NULL,
    unit_type       text NOT NULL,
    unit_number     text NOT NULL,
    place_code      text NOT NULL,

    PRIMARY KEY (snapshot_id, unit_type, unit_number, place_code),

    CONSTRAINT availability_seats_snapshot_fk
        FOREIGN KEY (snapshot_id)
        REFERENCES monitoring.availability_snapshots (id)
        ON DELETE CASCADE,

    CONSTRAINT availability_seats_unit_type_chk
        CHECK (length(trim(unit_type)) > 0),
    CONSTRAINT availability_seats_unit_number_chk
        CHECK (length(trim(unit_number)) > 0),
    CONSTRAINT availability_seats_place_code_chk
        CHECK (length(trim(place_code)) > 0)
);

CREATE INDEX availability_seats_snapshot_idx
    ON monitoring.availability_snapshot_seats (snapshot_id);

-- -----------------------------------------------------------------------------
-- Messaging
-- -----------------------------------------------------------------------------

CREATE TABLE messaging.notifications (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             uuid NOT NULL,
    subscription_id     uuid,
    notification_type   text NOT NULL,
    content             text NOT NULL,
    status              text NOT NULL DEFAULT 'PENDING',
    available_at        timestamptz NOT NULL DEFAULT now(),
    attempts            integer NOT NULL DEFAULT 0,
    locked_at           timestamptz,
    sent_at             timestamptz,
    last_error          text,
    created_at          timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT notifications_user_fk
        FOREIGN KEY (user_id)
        REFERENCES identity.users (id)
        ON DELETE CASCADE,

    CONSTRAINT notifications_subscription_fk
        FOREIGN KEY (subscription_id)
        REFERENCES monitoring.subscriptions (id)
        ON DELETE SET NULL,

    CONSTRAINT notifications_status_chk
        CHECK (status IN ('PENDING', 'PROCESSING', 'SENT', 'FAILED')),
    CONSTRAINT notifications_attempts_chk
        CHECK (attempts >= 0),
    CONSTRAINT notifications_type_chk
        CHECK (length(trim(notification_type)) > 0)
);

CREATE INDEX notifications_queue_idx
    ON messaging.notifications (status, available_at, id);
CREATE INDEX notifications_user_idx
    ON messaging.notifications (user_id, created_at DESC);

CREATE TABLE messaging.messages (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_user_id      uuid,
    receiver_user_id    uuid,
    content             text NOT NULL,
    sent_at             timestamptz NOT NULL DEFAULT now(),
    read_at             timestamptz,

    CONSTRAINT messages_sender_fk
        FOREIGN KEY (sender_user_id)
        REFERENCES identity.users (id)
        ON DELETE SET NULL,

    CONSTRAINT messages_receiver_fk
        FOREIGN KEY (receiver_user_id)
        REFERENCES identity.users (id)
        ON DELETE SET NULL,

    CONSTRAINT messages_content_chk
        CHECK (length(trim(content)) > 0)
);

CREATE INDEX messages_receiver_idx
    ON messaging.messages (receiver_user_id, sent_at DESC);
CREATE INDEX messages_sender_idx
    ON messaging.messages (sender_user_id, sent_at DESC);
CREATE INDEX messages_history_idx
    ON messaging.messages (sent_at DESC);

-- -----------------------------------------------------------------------------
-- Bot FSM state
-- -----------------------------------------------------------------------------

CREATE TABLE bot.conversation_sessions (
    user_id                 uuid PRIMARY KEY,
    current_command_code    integer,
    init_state              boolean NOT NULL DEFAULT false,
    context                 jsonb NOT NULL DEFAULT '{}'::jsonb,
    last_input_date         date,
    updated_at              timestamptz NOT NULL DEFAULT now(),
    expires_at              timestamptz,

    CONSTRAINT conversation_sessions_user_fk
        FOREIGN KEY (user_id)
        REFERENCES identity.users (id)
        ON DELETE CASCADE,
    CONSTRAINT conversation_sessions_context_object_chk
        CHECK (jsonb_typeof(context) = 'object')
);

CREATE INDEX conversation_sessions_expires_idx
    ON bot.conversation_sessions (expires_at)
    WHERE expires_at IS NOT NULL;

CREATE TRIGGER conversation_sessions_set_updated_at
BEFORE UPDATE ON bot.conversation_sessions
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- -----------------------------------------------------------------------------
-- Audit
-- -----------------------------------------------------------------------------

CREATE TABLE audit.audit_log (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id       uuid,
    action_code         text NOT NULL,
    entity_schema       text,
    entity_table        text,
    entity_id           text,
    old_values          jsonb,
    new_values          jsonb,
    source              text NOT NULL,
    correlation_id      uuid,
    created_at          timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT audit_actor_fk
        FOREIGN KEY (actor_user_id)
        REFERENCES identity.users (id)
        ON DELETE SET NULL,

    CONSTRAINT audit_action_chk
        CHECK (length(trim(action_code)) > 0),
    CONSTRAINT audit_source_chk
        CHECK (source IN ('BOT', 'MONITOR', 'NOTIFIER', 'ADMIN'))
);

CREATE INDEX audit_actor_created_idx
    ON audit.audit_log (actor_user_id, created_at DESC);
CREATE INDEX audit_entity_created_idx
    ON audit.audit_log (entity_table, entity_id, created_at DESC);
CREATE INDEX audit_action_created_idx
    ON audit.audit_log (action_code, created_at DESC);

COMMIT;
