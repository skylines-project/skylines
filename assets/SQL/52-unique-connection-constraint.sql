ALTER TABLE followers ADD CONSTRAINT unique_connection UNIQUE (source_id, destination_id);
