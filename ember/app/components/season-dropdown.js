import Component from '@ember/component';

export default Component.extend({
  tagName: '',
  year: null,

  init() {
    this._super(...arguments);

    let year = new Date().getFullYear();
    this.set('recentYears', [0, 1, 2, 3, 4].map(i => year - i));
  },
});
