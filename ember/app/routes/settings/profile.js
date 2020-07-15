import Route from '@ember/routing/route';

export default class ProfileRoute extends Route {
  model() {
    return this.modelFor('settings');
  }
}
