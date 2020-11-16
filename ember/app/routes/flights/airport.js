import BaseRoute from './-base';

export default class AirportRoute extends BaseRoute {
  getURL({ airport_id }) {
    return `/api/flights/airport/${airport_id}`;
  }
}
