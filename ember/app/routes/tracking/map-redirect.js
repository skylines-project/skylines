import Route from '@ember/routing/route';

export default class MapRedirectRoute extends Route {
  redirect({ user_ids }) {
    this.transitionTo('tracking.details', user_ids);
  }
}
