import { inject as service } from '@ember/service';

import BaseRoute from './-base';

export default class PinnedRoute extends BaseRoute {
  @service pinnedFlights;

  model(params) {
    let pinned = this.get('pinnedFlights.pinned') || [];
    if (pinned.length === 0) {
      return { count: 0, flights: [] };
    }

    return this.ajax.request(`/api/flights/list/${pinned.join(',')}`, {
      data: {
        page: params.page,
        column: params.column,
        order: params.order,
      },
    });
  }
}
