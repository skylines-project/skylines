import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({wildcard}) {
    return this.get('ajax').request(`/statistics/${wildcard}`).then(model => {
      if (wildcard) {
        let data = wildcard.split('/');
        Ember.set(model, data[0], parseInt(data[1], 10));
      }
      return model;
    });
  },
});
