def add_fixtures(db_session, *fixtures):
    db_session.add_all(fixtures)
    db_session.commit()
