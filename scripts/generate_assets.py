#!/usr/bin/env python

import os
import gzip
from argparse import ArgumentParser
from config import to_envvar

# Create argument parser
parser = ArgumentParser(description='Generate concatenated and minified CSS and JS assets.')
parser.add_argument('conf_path', nargs='?', metavar='config.ini',
                    help='path to the configuration INI file')

# Parse arguments
args = parser.parse_args()

# Load config from file
if not to_envvar(args.conf_path):
    parser.error('Config file "{}" not found.'.format(args.conf_path))

# Create assets environment
from skylines import app
app.add_assets()

# Generate the assets/bundles
for bundle in app.assets:
    print 'Generating bundle: {}'.format(bundle.output)
    bundle.build()

    # Generate GZipped bundles for nginx static gzip serving
    bundle_path = bundle.resolve_output()
    compressed_path = bundle_path + '.gz'
    print 'Compressing bundle: {} -> {}'.format(os.path.basename(bundle_path),
                                                os.path.basename(compressed_path))
    with open(bundle_path, 'rb') as f_in, \
            gzip.open(compressed_path, 'wb') as f_out:
        f_out.writelines(f_in)
