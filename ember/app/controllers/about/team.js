import Ember from 'ember';

export default Ember.Controller.extend({
  intl: Ember.inject.service(),

  text: Ember.computed('model.content', 'intl.locale', function() {
    let intl = this.get('intl');

    return this.get('model.content')
      .replace('Developers', intl.t('developers'))
      .replace('Translators', intl.t('translators'));
  }),
});
