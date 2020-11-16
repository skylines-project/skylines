import BaseRoute from './-base';

export default class DateRoute extends BaseRoute {
  getURL({ date }) {
    return `/api/flights/date/${date}`;
  }
}
