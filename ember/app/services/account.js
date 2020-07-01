import { computed, getProperties } from '@ember/object';
import { alias } from '@ember/object/computed';
import Service, { inject as service } from '@ember/service';

export default class AccountService extends Service {
  @service session;
  @alias('session.data.authenticated.settings') sessionData;

  @computed('sessionData.{id,name}')
  get user() {
    let sessionData = this.sessionData;
    if (sessionData) {
      return getProperties(sessionData, 'id', 'name');
    }
  }

  @alias('sessionData.club') club;
}
