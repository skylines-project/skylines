import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ club_id }) {
    return `/api/groupflights/club/${club_id}`;
  },
});
