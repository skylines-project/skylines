import * as Notifications from './route-handlers/notifications';
import * as Settings from './route-handlers/settings';
import * as Users from './route-handlers/users';

export default function () {
  this.passthrough('/translations/**');

  this.get('/api/locale', { locale: 'en' });

  Notifications.register(this);
  Settings.register(this);
  Users.register(this);
}
