import Ember from 'ember';

export default Ember.Controller.extend({
  queryParams: ['year'],
  year: (new Date()).getFullYear().toString(),
});
