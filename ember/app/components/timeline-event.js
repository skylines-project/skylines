import Component from '@ember/component';

import computedComponent from '../computed/computed-component';

export default class TimelineEvent extends Component {
  tagName = '';

  event = null;

  @computedComponent('event.type', 'timeline-events/') eventComponent;
}
