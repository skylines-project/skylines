import { action } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@glimmer/component';

import screenfull from 'screenfull';

export default class FullscreenButton extends Component {
  @service intl;
  @service notifications;

  @action toggle() {
    if (screenfull.isEnabled) {
      let element = this.args.fullscreenElement;
      screenfull.toggle(document.querySelector(element));
    } else {
      this.notifications.warning(this.intl.t('fullscreen-not-supported'));
    }
  }
}
