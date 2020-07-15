import BaseRoute from './-base';

export default class UnassignedRoute extends BaseRoute {
  getURL() {
    return '/api/flights/unassigned';
  }
}
