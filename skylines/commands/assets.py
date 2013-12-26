from flask.ext.script import Manager

import os.path
import gzip
from flask import current_app

manager = Manager(help="Perform operations related to the JS/CSS assets")


@manager.command
def build():
    current_app.add_assets()

    # Generate the assets/bundles
    for bundle in current_app.assets:
        print 'Generating bundle: {}'.format(bundle.output)
        bundle.build()

        # Generate GZipped bundles for nginx static gzip serving
        bundle_path = bundle.resolve_output()
        compressed_path = bundle_path + '.gz'

        print 'Compressing bundle: {} -> {}'.format(
            os.path.basename(bundle_path), os.path.basename(compressed_path))

        with open(bundle_path, 'rb') as f_in, \
                gzip.open(compressed_path, 'wb') as f_out:
            f_out.writelines(f_in)
