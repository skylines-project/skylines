import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ pilot_id }) {
    return `/api/flights/pilot/${pilot_id}`;
  },
});
