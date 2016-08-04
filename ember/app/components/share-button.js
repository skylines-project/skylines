/* global getShareUrl */

import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'span',

  didInsertElement() {
    let url = getShareUrl(location.origin + location.pathname);

    let content = `<div style="text-align:center">
      <input value="${url}" type="text" class="form-control" style="margin-bottom:9px">
      <a href="https://www.facebook.com/share.php?u=${url}" target="_blank" class="btn btn-default btn-xs"><i class="icon-facebook"> Share</i></a>
      <a href="https://plus.google.com/share?url=${url}" target="_blank" class="btn btn-default btn-xs"><i class="icon-google-plus"> Share</i></a>
      <a href="https://twitter.com/share?url=${url}" target="_blank" class="btn btn-default btn-xs"><i class="icon-twitter"> Tweet</i></a>
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
});
