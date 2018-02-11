import Component from '@ember/component';

import computedComponent from '../computed/computed-component';

export default Component.extend({
  tagName: '',

  event: null,

  eventComponent: computedComponent('event.type', 'timeline-events/'),
});
