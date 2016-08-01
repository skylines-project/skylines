import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ date }) {
    return `/flights/date/${date}`;
  },
});
