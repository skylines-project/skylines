import BaseRoute from './-base';

export default class PilotRoute extends BaseRoute {
  getURL({ pilot_id }) {
    return `/api/statistics/pilot/${pilot_id}`;
  }
}
