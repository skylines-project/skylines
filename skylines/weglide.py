# -*- coding: utf-8 -*-

import logging
import requests
import sentry_sdk

from skylines.database import db
from skylines.lib.files import open_file
from skylines.model import IGCFile

log = logging.getLogger(__name__)


def upload(igc_file_id, weglide_user_id, weglide_birthday):
    with sentry_sdk.push_scope() as scope:
        scope.set_context(
            "WeGlide Upload",
            {
                "igc_file_id": igc_file_id,
                "weglide_user_id": weglide_user_id,
            },
        )

        log.info(
            "Uploading IGC file %s to WeGlide for user %s…",
            igc_file_id,
            weglide_user_id,
        )

        igc_file = db.session.query(IGCFile).get(igc_file_id)
        if not igc_file:
            # missing IGCFile in the database is logged and sent to Sentry
            log.warn(
                "IGC file (%s) upload failed because it can not be found in the database",
                igc_file_id,
            )
            sentry_sdk.capture_message(
                "IGC file can not be found in the database", "warning"
            )
            return False

        try:
            with open_file(igc_file.filename) as f:
                data = {"user_id": weglide_user_id, "date_of_birth": weglide_birthday}
                files = {"file": (igc_file.filename, f)}

                response = requests.post(
                    "https://api.weglide.org/v1/igcfile",
                    data=data,
                    files=files,
                    timeout=30,
                )

                igc_file.weglide_status = response.status_code
                try:
                    igc_file.weglide_data = response.json()
                except ValueError:
                    # `igc_file.weglide_data` is already `None` so we don't have to do anything
                    pass

                db.session.commit()

                if 200 <= response.status_code < 300:
                    log.info("%s: WeGlide IGC file upload successful", igc_file)
                else:
                    log.warn(
                        "%s: WeGlide IGC file upload failed (HTTP %d)",
                        igc_file,
                        response.status_code,
                    )

                return True

        except requests.exceptions.RequestException:
            # network errors are an expected failure so we only log them as warnings and move on... 🤷‍
            log.warn("%s: WeGlide IGC file upload failed", igc_file, exc_info=True)

        except Exception:
            # unexpected errors are logged and sent to Sentry
            log.error("%s: WeGlide IGC file upload failed", igc_file, exc_info=True)
            sentry_sdk.capture_exception()

        igc_file.weglide_status = 2
        db.session.commit()
