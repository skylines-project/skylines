import { inject as service } from '@ember/service';
import Component from '@glimmer/component';

export default class NotificationsBadge extends Component {
  @service notificationCounter;
  @service intl;
}
