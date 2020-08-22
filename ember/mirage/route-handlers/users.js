import { Response } from 'ember-cli-mirage';

import { getSession } from '../utils/session';

export function register(server) {
  server.get('/api/users/:id');

  server.post('/api/users/check-email', function (schema, request) {
    let { user } = getSession(schema);

    let json;
    try {
      json = JSON.parse(request.requestBody);
    } catch (error) {
      return new Response(400, {}, { error: 'invalid-request' });
    }

    let { email } = json;

    let result = 'available';
    if (user && email === user.email) {
      result = 'self';
    } else if (schema.users.findBy({ email })) {
      result = 'unavailable';
    }

    return new Response(200, {}, { result });
  });
}
