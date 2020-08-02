import { Response } from 'ember-cli-mirage';

import { getSession } from './utils/session';

export default function () {
  this.passthrough('/translations/**');

  this.get('/api/locale', { locale: 'en' });

  this.get('/api/notifications', { events: [] });

  this.get('/api/settings', function (schema) {
    let { user } = getSession(schema);
    if (!user) {
      return new Response(401, {}, { error: 'invalid-token' });
    }

    let serialized = this.serialize(user, 'user');
    return serialized.user;
  });
}
