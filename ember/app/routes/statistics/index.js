import BaseRoute from './-base';

export default class IndexRoute extends BaseRoute {
  getURL() {
    return '/api/statistics/';
  }
}
