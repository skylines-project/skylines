import Ember from 'ember';

export default Ember.Route.extend({
  redirect({ user_ids }) {
    this.redirectTo('tracking.details', user_ids);
  },
});
