import { computed } from '@ember/object';

import Base from './-base';

export default class NewUser extends Base {
  @computed('accountUserIsActor')
  get translationKey() {
    let i = this.accountUserIsActor ? 2 : 1;
    return `timeline-events.new-user.message${i}`;
  }
}
