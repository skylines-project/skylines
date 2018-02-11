import Route from '@ember/routing/route';

export default Route.extend({
  redirect({ user_ids }) {
    this.transitionTo('tracking.details', user_ids);
  },
});
