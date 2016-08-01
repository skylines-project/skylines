import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ club_id }) {
    return `/flights/club/${club_id}`;
  },
});
