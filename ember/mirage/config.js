import * as Notifications from './route-handlers/notifications';
import * as Settings from './route-handlers/settings';

export default function () {
  this.passthrough('/translations/**');

  this.get('/api/locale', { locale: 'en' });

  Notifications.register(this);
  Settings.register(this);
}
