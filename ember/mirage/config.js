import * as Settings from './route-handlers/settings';

export default function () {
  this.passthrough('/translations/**');

  this.get('/api/locale', { locale: 'en' });

  this.get('/api/notifications', { events: [] });

  Settings.register(this);
}
