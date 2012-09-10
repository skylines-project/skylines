CREATE TABLE notifications
(
  id serial NOT NULL,
  time_created timestamp without time zone NOT NULL,
  time_read timestamp without time zone,
  sender_id integer NOT NULL,
  recipient_id integer NOT NULL,
  flight_id integer,
  flight_comment_id integer,
  CONSTRAINT notifications_pkey PRIMARY KEY (id ),
  CONSTRAINT notifications_sender_id_fkey FOREIGN KEY (sender_id)
      REFERENCES tg_user (user_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT notifications_recipient_id_fkey FOREIGN KEY (recipient_id)
      REFERENCES tg_user (user_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT notifications_flight_id_fkey FOREIGN KEY (flight_id)
      REFERENCES flights (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT notifications_flight_comment_id_fkey FOREIGN KEY (flight_comment_id)
      REFERENCES flight_comments (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);

