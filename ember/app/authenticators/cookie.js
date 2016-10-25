import Ember from 'ember';
import Base from 'ember-simple-auth/authenticators/base';

export default Base.extend({
  ajax: Ember.inject.service(),

  authenticate(email, password) {
    return this.get('ajax').request('/api/session', { method: 'PUT', json: { email, password } })
      .then(() => this.get('ajax').request('/api/settings/'))
      .then(settings => ({ settings }));
  },

  restore(/* data */) {
    return this.get('ajax').request('/api/settings/')
      .then(settings => ({ settings }));
  },

  invalidate(/* data */) {
    return this.get('ajax').request('/api/session', { method: 'DELETE' });
  },
});
