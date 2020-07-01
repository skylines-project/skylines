import Service, { inject as service } from '@ember/service';

export default class PinnedFlights extends Service {
  @service cookies;

  constructor() {
    super(...arguments);
    this.load();
  }

  pin(id) {
    this.set('pinned', this.pinned.concat([id]));
    this.save();
  }

  unpin(id) {
    this.set('pinned', this.pinned.without(id));
    this.save();
  }

  load() {
    let pinned = [];

    let cookie = this.cookies.read('SkyLines_pinnedFlights');
    if (cookie) {
      pinned = cookie.split(',').map(it => parseInt(it, 10));
    }

    this.set('pinned', pinned);
  }

  save() {
    this.cookies.write('SkyLines_pinnedFlights', this.pinned.join(','), { path: '/' });
  }

  toggle(id) {
    if (this.pinned.includes(id)) {
      this.unpin(id);
    } else {
      this.pin(id);
    }
  }
}
