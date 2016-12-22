import RavenLogger from 'ember-cli-sentry/services/raven';

export default RavenLogger.extend({
  ignoreError(error) {
    return error && error.name === 'TransitionAborted';
  },
});
