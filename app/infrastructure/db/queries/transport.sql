-- name: get_provider_by_code(code)^
SELECT id, code, name, adapter_code, base_url, is_active, created_at, updated_at FROM transport.providers WHERE code = :code;

-- name: insert_provider(id, code, name, adapter_code, base_url, is_active)!
INSERT INTO transport.providers (id, code, name, adapter_code, base_url, is_active)
VALUES (:id, :code, :name, :adapter_code, :base_url, :is_active);

-- name: get_stop_by_provider_and_code(provider_id, external_code)^
SELECT id, provider_id, external_code, name, latitude, longitude, created_at, updated_at
FROM transport.stops WHERE provider_id = :provider_id AND external_code = :external_code;

-- name: insert_stop(id, provider_id, external_code, name, latitude, longitude)!
INSERT INTO transport.stops (id, provider_id, external_code, name, latitude, longitude)
VALUES (:id, :provider_id, :external_code, :name, :latitude, :longitude);

-- name: update_stop_name(name, stop_id)!
UPDATE transport.stops SET name = :name WHERE id = :stop_id;

-- name: get_stop_by_id(stop_id)^
SELECT id, provider_id, external_code, name, latitude, longitude, created_at, updated_at FROM transport.stops WHERE id = :stop_id;

-- name: get_route_by_stops(from_stop_id, to_stop_id)^
SELECT id, from_stop_id, to_stop_id, created_at, updated_at FROM transport.routes
WHERE from_stop_id = :from_stop_id AND to_stop_id = :to_stop_id;

-- name: insert_route(id, from_stop_id, to_stop_id)!
INSERT INTO transport.routes (id, from_stop_id, to_stop_id) VALUES (:id, :from_stop_id, :to_stop_id);

-- name: get_service_by_number_and_route(external_number, route_id)^
SELECT id, provider_id, route_id, transport_mode, external_number, service_type, days_rule, days_exceptions, valid_from, valid_to, created_at, updated_at FROM transport.services WHERE external_number = :external_number AND route_id = :route_id;

-- name: insert_service(id, provider_id, route_id, transport_mode, external_number, service_type, days_rule, days_exceptions)!
INSERT INTO transport.services (id, provider_id, route_id, transport_mode, external_number, service_type, days_rule, days_exceptions)
VALUES (:id, :provider_id, :route_id, :transport_mode, :external_number, :service_type, :days_rule, :days_exceptions) RETURNING id;

-- name: update_service(transport_mode, service_type, days_rule, days_exceptions, service_id)!
UPDATE transport.services SET transport_mode = :transport_mode, service_type = :service_type, days_rule = :days_rule, days_exceptions = :days_exceptions
WHERE id = :service_id;

-- name: get_service_route_by_service_and_route(service_id, route_id)^
SELECT id, service_id, route_id, departure_time, arrival_time, duration_minutes, created_at, updated_at
FROM transport.service_routes
WHERE service_id = :service_id AND route_id = :route_id;

-- name: insert_service_route(id, service_id, route_id, departure_time, arrival_time, duration_minutes)!
INSERT INTO transport.service_routes (id, service_id, route_id, departure_time, arrival_time, duration_minutes)
VALUES (:id, :service_id, :route_id, :departure_time, :arrival_time, :duration_minutes) RETURNING id;

-- name: update_service_route_times(departure_time, arrival_time, duration_minutes, service_route_id)!
UPDATE transport.service_routes SET departure_time = :departure_time, arrival_time = :arrival_time, duration_minutes = :duration_minutes
WHERE id = :service_route_id;

-- name: get_service_route_by_id(service_route_id)^
SELECT id, service_id, route_id, departure_time, arrival_time, duration_minutes, created_at, updated_at
FROM transport.service_routes WHERE id = :service_route_id;

-- name: get_service_by_id(service_id)^
SELECT id, provider_id, route_id, transport_mode, external_number, service_type, days_rule, days_exceptions, valid_from, valid_to, created_at, updated_at
FROM transport.services WHERE id = :service_id;

-- name: get_route_by_id(route_id)^
SELECT id, from_stop_id, to_stop_id, created_at, updated_at FROM transport.routes WHERE id = :route_id;
