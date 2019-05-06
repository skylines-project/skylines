import Controller from '@ember/controller';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Controller.extend({
  intl: service(),

  text: computed('model.content', 'intl.locale', function() {
    let intl = this.intl;

    return this.get('model.content')
      .replace('Developers', intl.t('developers'))
      .replace('Translators', intl.t('translators'));
  }),
});
