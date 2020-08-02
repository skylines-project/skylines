import * as Clubs from './route-handlers/clubs';
import * as Notifications from './route-handlers/notifications';
import * as Settings from './route-handlers/settings';
import * as Users from './route-handlers/users';

export default function () {
  this.passthrough('/translations/**');

  this.get('/api/locale', { locale: 'en' });

  Clubs.register(this);
  Notifications.register(this);
  Settings.register(this);
  Users.register(this);
}
