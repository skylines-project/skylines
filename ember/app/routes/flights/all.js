import BaseRoute from './-base';

export default class AllRoute extends BaseRoute {
  getURL() {
    return '/api/flights/all';
  }
}
