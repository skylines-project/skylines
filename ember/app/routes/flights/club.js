import BaseRoute from './-base';

export default class ClubRoute extends BaseRoute {
  getURL({ club_id }) {
    return `/api/flights/club/${club_id}`;
  }
}
