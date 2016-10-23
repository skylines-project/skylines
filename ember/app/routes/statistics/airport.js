import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ airport_id }) {
    return `/api/statistics/airport/${airport_id}`;
  },
});
