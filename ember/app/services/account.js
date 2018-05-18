import { computed, getProperties } from '@ember/object';
import { alias } from '@ember/object/computed';
import Service, { inject as service } from '@ember/service';

export default Service.extend({
  session: service(),
  sessionData: alias('session.data.authenticated.settings'),

  user: computed('sessionData.{id,name}', function() {
    let sessionData = this.sessionData;
    if (sessionData) {
      return getProperties(sessionData, 'id', 'name');
    }
  }),

  club: alias('sessionData.club'),
});
