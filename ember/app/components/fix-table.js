import { action, computed } from '@ember/object';
import Component from '@glimmer/component';

export default class extends Component {
  @computed('args.fixes.@each.flight')
  get data() {
    return this.args.fixes.map((fix, i) => {
      let flight = fix.get('flight');
      let id = flight.get('id');
      let color = flight.get('color');
      let competitionId = flight.get('competition_id') || flight.get('registration');
      let removable = i !== 0;
      return { id, color, competitionId, removable, fix };
    });
  }

  @computed('data.[]')
  get selectable() {
    return this.data.length > 1;
  }

  @action
  select(id) {
    this.args.onSelectionChange(this.args.selection === id ? null : id);
  }
}
