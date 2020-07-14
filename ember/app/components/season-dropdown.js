import Component from '@glimmer/component';

const YEAR = new Date().getFullYear();

export default class SeasonDropdown extends Component {
  recentYears = [0, 1, 2, 3, 4].map(i => YEAR - i);
}
