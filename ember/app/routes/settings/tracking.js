import Route from '@ember/routing/route';

export default class TrackingRoute extends Route {
  model() {
    return this.modelFor('settings');
  }
}
