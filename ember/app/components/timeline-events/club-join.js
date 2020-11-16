import { computed } from '@ember/object';

import Base from './-base';

export default class ClubJoin extends Base {
  @computed('accountUserIsActor')
  get translationKey() {
    let i = this.accountUserIsActor ? 2 : 1;
    return `timeline-events.club-join.message${i}`;
  }
}
