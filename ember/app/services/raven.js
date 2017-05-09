import RavenLogger from 'ember-cli-sentry/services/raven';
import { isAbortError } from 'ember-ajax/errors';

export default RavenLogger.extend({
  ignoreError(error) {
    return isAbortError(error);
  },
});
