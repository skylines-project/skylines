import AjaxService from 'ember-ajax/services/ajax';

export default AjaxService.extend({
  options(url, options = {}) {
    if (options.json) {
      options.contentType = 'application/json';
      options.data = JSON.stringify(options.json);
      delete options.json;
    }

    return this._super(url, options);
  },
});
