import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ club_id }) {
    return `/api/statistics/club/${club_id}`;
  },
});
