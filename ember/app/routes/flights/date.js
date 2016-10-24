import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ date }) {
    return `/api/flights/date/${date}`;
  },
});
