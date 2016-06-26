import Ember from 'ember';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),

  classNames: ['panel panel-default'],

  key: null,
  pending: false,
  error: null,

  sendChangeRequest() {
    this.set('pending', true);
    this.get('ajax').request('/settings/tracking/key', { method: 'POST' }).then(({ key }) => {
      this.setProperties({ key, error: null });
    }).catch(error => {
      this.setProperties({ error });
    }).finally(() => {
      this.set('pending', false);
    });
  },

  actions: {
    submit() {
      this.sendChangeRequest();
    },
  },
});
