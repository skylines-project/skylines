import { getContext } from '@ember/test-helpers';

import { authenticateSession } from 'ember-simple-auth/test-support';

export async function authenticateAs(user) {
  let { owner, server } = getContext();

  server.create('mirage-session', { user });

  await authenticateSession();
  await owner.lookup('service:account').loadSettings();
}
