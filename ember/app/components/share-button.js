import Ember from 'ember';

export default Ember.Component.extend({
  pinnedFlights: Ember.inject.service(),

  tagName: 'span',

  didInsertElement() {
    let url = this.getShareUrl(location.origin + location.pathname);

    let content = `<div style="text-align:center">
      <input value="${url}" type="text" class="form-control" style="margin-bottom:9px">
      <a href="https://www.facebook.com/share.php?u=${url}" target="_blank" class="btn btn-default btn-xs"><i class="fa fa-facebook"> Share</i></a>
      <a href="https://plus.google.com/share?url=${url}" target="_blank" class="btn btn-default btn-xs"><i class="fa fa-google-plus"> Share</i></a>
      <a href="https://twitter.com/share?url=${url}" target="_blank" class="btn btn-default btn-xs"><i class="fa fa-twitter"> Tweet</i></a>
    </div>`;

    let popover_template = `<div class="popover" style="white-space: nowrap; z-index: 5000;">
      <div class="arrow"></div>
      <h3 class="popover-title"></h3>
      <div class="popover-content"></div>
    </div>`;

    this.$('.btn-share').popover({
      trigger: 'click',
      container: '#fullscreen-content',
      content,
      title: 'Spread the word',
      placement: 'bottom',
      html: true,
      template: popover_template,
    });
  },

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
