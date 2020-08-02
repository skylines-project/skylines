import { Response } from 'ember-cli-mirage';

import { getSession } from '../utils/session';

export function register(server) {
  server.get('/api/settings', function (schema) {
    let { user } = getSession(schema);
    if (!user) {
      return new Response(401, {}, { error: 'invalid-token' });
    }

    let serialized = this.serialize(user, 'user');
    return serialized.user;
  });
}
