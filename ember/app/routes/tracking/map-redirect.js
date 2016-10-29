import Ember from 'ember';

export default Ember.Route.extend({
  redirect({ user_ids }) {
    this.transitionTo('tracking.details', user_ids);
  },
});
