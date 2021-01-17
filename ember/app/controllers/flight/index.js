import Controller from '@ember/controller';

export default class IndexController extends Controller {
  queryParams = ['baselayer', 'overlays'];
  baselayer = null;
  overlays = null;
}
