import config

config.to_envvar()

from skylines import create_combined_app

application = create_combined_app()
