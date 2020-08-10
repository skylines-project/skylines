import Component from '@ember/component';
import { inject as service } from '@ember/service';
import { tracked } from '@glimmer/tracking';

import { BASE_LAYERS, OVERLAY_LAYERS } from '../services/map-settings';

export default class LayerSwitcher extends Component {
  tagName = '';

  @service mapSettings;

  @tracked open = false;

  BASE_LAYERS = BASE_LAYERS;
  OVERLAY_LAYERS = OVERLAY_LAYERS;
}
