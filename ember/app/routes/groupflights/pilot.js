import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ pilot_id }) {
    return `/api/groupflights/pilot/${pilot_id}`;
  },
});
