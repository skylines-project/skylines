import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ pilot_id }) {
    return `/flights/pilot/${pilot_id}`;
  },
});
