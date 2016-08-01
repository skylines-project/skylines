import Ember from 'ember';

export default Ember.Route.extend({
  queryParams: {
    year: { refreshModel: true },
  },

  model() {},
});
