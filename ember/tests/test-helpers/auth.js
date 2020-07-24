import { getContext } from '@ember/test-helpers';

import { authenticateSession } from 'ember-simple-auth/test-support';

export async function authenticateAs(user) {
  let userSerializer = getContext().server.serializerOrRegistry.serializerFor(user);

  await authenticateSession({
    settings: userSerializer.serialize(user).user,
  });
}
