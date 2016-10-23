import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ list }) {
    return `/api/flights/list/${list}`;
  },
});
