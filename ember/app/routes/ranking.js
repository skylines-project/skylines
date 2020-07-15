import Route from '@ember/routing/route';

export default class RankingRoute extends Route {
  queryParams = {
    year: { refreshModel: true },
  };

  model() {}
}
