import { computed } from '@ember/object';

import Base from './-base';

export default class FlightUpload extends Base {
  @computed('accountUserIsActor')
  get translationKey() {
    let i = this.accountUserIsActor ? 2 : 1;
    return `timeline-events.flight-upload.message${i}`;
  }
}
