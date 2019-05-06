import Controller from '@ember/controller';
import { readOnly } from '@ember/object/computed';
import { inject as service } from '@ember/service';

export default Controller.extend({
  account: service(),

  name: readOnly('model.name'),
  years: readOnly('model.years'),
  sumPilots: readOnly('model.sumPilots'),
});
