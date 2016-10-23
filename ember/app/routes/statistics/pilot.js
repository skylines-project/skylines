import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ pilot_id }) {
    return `/statistics/pilot/${pilot_id}`;
  },
});
