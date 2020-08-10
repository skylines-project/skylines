import Component from '@glimmer/component';

import computedComponent from '../computed/computed-component';

export default class TimelineEvent extends Component {
  @computedComponent('args.event.type', 'timeline-events/') eventComponent;
}
