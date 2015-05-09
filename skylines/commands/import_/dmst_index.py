from flask.ext.script import Command, Option

import re
from skylines.database import db
from skylines.model import AircraftModel

r = re.compile(r'^(.*?)\s*\.+[\.\s]*(\d+)\s*$')


class DMStIndex(Command):
    """ Add or update dmst handicaps in SkyLines """

    option_list = (
        Option('path', help='DMSt index list file'),
    )

    def run(self, path):
        for line in file(path):
            m = r.match(line)
            if m:
                names, index = m.group(1), int(m.group(2))
                for name in names.split(';'):
                    name = name.strip().decode('utf-8')
                    model = AircraftModel.by_name(name)
                    if model is None:
                        model = AircraftModel(name=name)
                        model.kind = 1
                        db.session.add(model)
                    model.dmst_index = index

        db.session.commit()
