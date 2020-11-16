import BaseRoute from './-base';

export default class LatestRoute extends BaseRoute {
  getURL() {
    return '/api/flights/latest';
  }
}
