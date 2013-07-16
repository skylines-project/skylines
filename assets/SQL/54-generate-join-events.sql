INSERT INTO events (type, time, actor_id)
  SELECT 4, created, id
  FROM tg_user
