import BaseRoute from './-base';

export default BaseRoute.extend({
  getURL() {
    return '/api/groupflights/all';
  },
});
