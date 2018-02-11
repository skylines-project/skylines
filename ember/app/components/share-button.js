import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
  pinnedFlights: service(),

  tagName: '',

  url: computed(function() {
    return this.getShareUrl(location.origin + location.pathname);
  }),

  /**
   * Returns the URL for the current page and add pinned flights
   * to the URL which are only stored client-side inside a cookie.
   *
   * @param {String} url The original URL.
   * @return {String} URL for the current flights including pinned flights.
   */
  getShareUrl(url) {
    let pinnedFlights = this.get('pinnedFlights.pinned');

    let url_re = /(.*?)\/([\d,]{1,})/;
    let url_split = url_re.exec(url);

    let url_ids = url_split[2].split(',').map(it => parseInt(it, 10));
    let unique_ids = url_ids.concat(pinnedFlights).uniq();

    return `${url_split[1]}/${unique_ids.join(',')}`;
  },
});
