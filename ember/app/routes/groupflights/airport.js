import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ airport_id }) {
    return `/api/flights/airport/${airport_id}`;
  },
});
