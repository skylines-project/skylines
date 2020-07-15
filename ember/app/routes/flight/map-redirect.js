import Route from '@ember/routing/route';

export default class MapRedirectRoute extends Route {
  redirect() {
    this.replaceWith('flight.index');
  }
}
