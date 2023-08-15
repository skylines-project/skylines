import * as Sentry from '@sentry/browser';
import { Ember } from '@sentry/integrations/esm/ember';

import config from './config/environment';

export function startSentry() {
  let integrations = [];
  if (config.environment === 'production') {
    integrations.push(new Ember());
  }

  Sentry.init({
    ...config.sentry,
    integrations,

    beforeSend(event, hint) {
      let error = hint.originalException;

      if (error) {
        // ignore cancellation errors from the Ember router of ember-concurrency
        if (error.name === 'TaskCancelation' || error.name === 'TransitionAborted') {
          return null;
        }
      }

      return event;
    },
  });
}
