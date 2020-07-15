import BaseRoute from './-base';

export default class AirportRoute extends BaseRoute {
  getURL({ airport_id }) {
    return `/api/statistics/airport/${airport_id}`;
  }
}
