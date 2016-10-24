import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ club_id }) {
    return `/api/flights/club/${club_id}`;
  },
});
