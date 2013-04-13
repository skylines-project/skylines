UPDATE flights SET locations = ST_SetSRID(locations, 4326);
