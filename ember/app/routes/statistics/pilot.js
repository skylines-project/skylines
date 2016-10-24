import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ pilot_id }) {
    return `/api/statistics/pilot/${pilot_id}`;
  },
});
