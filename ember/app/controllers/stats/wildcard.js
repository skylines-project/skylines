import Controller from '@ember/controller';
import { readOnly } from '@ember/object/computed';
import { inject as service } from '@ember/service';

export default class WildcardController extends Controller {
  @service account;

  @readOnly('model.name') name;
  @readOnly('model.years') years;
  @readOnly('model.sumPilots') sumPilots;
}
