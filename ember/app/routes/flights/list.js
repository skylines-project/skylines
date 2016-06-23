import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({list}) {
    return `/flights/list/${list}`;
  },
});
