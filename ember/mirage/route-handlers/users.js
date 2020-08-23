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

  server.post('/api/users/recover', function (schema, request) {
    let { user: currentUser } = getSession(schema);

    let json;
    try {
      json = JSON.parse(request.requestBody);
    } catch (error) {
      return new Response(400, {}, { error: 'invalid-request' });
    }

    if ('recoveryKey' in json) {
      let { password, recoveryKey } = json;
      if (!password || !recoveryKey) {
        return new Response(422, {}, { error: 'validation-failed' });
      }

      let user = schema.users.findBy({ recoveryKey });
      if (!user) {
        return new Response(422, {}, { error: 'recovery-key-unknown' });
      }

      user.update({ password, recoveryKey: null });

      return {};
    } else {
      let { email } = json;
      if (!email) {
        return new Response(422, {}, { error: 'validation-failed' });
      }

      let user = schema.users.findBy({ email });
      if (!user) {
        return new Response(422, {}, { error: 'email-unknown' });
      }

      user.update({ recoveryKey: 'abc123def' });

      if (currentUser?.admin) {
        let url = `http://skylines.aero/users/recover?key=${user.recoveryKey}`;
        return { url };
      } else {
        return {};
      }
    }
  });
}
