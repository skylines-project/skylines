import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL({ list }) {
    return `/api/groupflights/list/${list}`;
  },
});
