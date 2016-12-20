import Ember from 'ember';

export default Ember.Route.extend({
  redirect() {
    this.replaceWith('ranking.clubs');
  },
});
