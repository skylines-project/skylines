import { isAbortError } from 'ember-ajax/errors';
import RavenLogger from 'ember-cli-sentry/services/raven';

import config from 'skylines/config/environment';

const { release } = config.sentry;

export default RavenLogger.extend({
  release,

  ignoreError(error) {
    return isAbortError(error);
  },
});
