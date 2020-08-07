import Service from '@ember/service';

class MockCookiesService extends Service {
  data = new Map();

  read(name) {
    if (name) {
      return this.data.get(name);
    } else {
      let all = {};
      this.data.forEach((value, key) => (all[key] = value));
      return all;
    }
  }

  write(name, value) {
    this.data.set(name, value);
  }

  clear(name) {
    this.data.delete(name);
  }

  exists(name) {
    this.data.has(name);
  }
}

export function setupMockCookies(hooks) {
  hooks.beforeEach(function () {
    this.owner.unregister('service:cookies');
    this.owner.register('service:cookies', MockCookiesService);
  });
}
