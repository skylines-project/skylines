import { isAbortError } from 'ember-ajax/errors';
import RavenLogger from 'ember-cli-sentry/services/raven';

export default RavenLogger.extend({
  ignoreError(error) {
    return isAbortError(error);
  },
});
