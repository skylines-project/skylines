import BaseRoute from './-base';

export default class ListRoute extends BaseRoute {
  getURL({ list }) {
    return `/api/flights/list/${list}`;
  }
}
