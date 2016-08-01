import Ember from 'ember';

import computedComponent from '../utils/computed-component';

export default Ember.Component.extend({
  tagName: '',

  event: null,

  eventComponent: computedComponent('event.type', 'timeline-events/'),
});
