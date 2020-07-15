import Controller from '@ember/controller';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default class TeamController extends Controller {
  @service intl;

  @computed('model.content', 'intl.locale')
  get text() {
    let intl = this.intl;

    return this.get('model.content')
      .replace('Developers', intl.t('developers'))
      .replace('Translators', intl.t('translators'));
  }
}
