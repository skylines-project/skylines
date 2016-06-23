import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({airport_id}) {
    return `/flights/airport/${airport_id}`;
  },
});
