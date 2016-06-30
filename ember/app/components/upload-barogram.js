import BarogramComponent from './base-barogram';

export default BarogramComponent.extend({
  prefix: null,
  uploadMode: true,
  height: 160,

  init() {
    this._super(...arguments);
    window[`barogram-${this.get('prefix')}`] = this;
  },
});
