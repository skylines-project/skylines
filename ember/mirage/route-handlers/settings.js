import { Response } from 'ember-cli-mirage';

import { getSession } from '../utils/session';

export function register(server) {
  server.get('/api/settings', function (schema) {
    let { user } = getSession(schema);
    if (!user) {
      return new Response(401, {}, { error: 'invalid-token' });
    }

    return user;
  });

  server.post('/api/settings', function (schema, request) {
    let { user } = getSession(schema);
    if (!user) {
      return new Response(401, {}, { error: 'invalid-token' });
    }

    let data = JSON.parse(request.requestBody);

    if ('email' in data) {
      let { email } = data;
      if (email !== user.email && schema.users.findBy({ email })) {
        return new Response(422, {}, { error: 'email-exists-already' });
      }

      user.update({ email });
    }

    const simpleFields = [
      'altitudeUnit',
      'distanceUnit',
      'firstName',
      'lastName',
      'liftUnit',
      'speedUnit',
      'trackingCallsign',
      'trackingDelay',
    ];
    for (let key of simpleFields) {
      if (key in data) {
        user.update({ [key]: data[key] });
      }
    }

    // TODO password update
    // TODO club update

    return new Response(200, {}, {});
  });
}
