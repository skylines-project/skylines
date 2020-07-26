import { getContext } from '@ember/test-helpers';

import { authenticateSession } from 'ember-simple-auth/test-support';

export async function authenticateAs(user) {
  let { owner, server } = getContext();

  let userSerializer = server.serializerOrRegistry.serializerFor(user);

  server.get('/api/settings', userSerializer.serialize(user).user);

  await authenticateSession();
  await owner.lookup('service:account').loadSettings();
}
