import Controller from '@ember/controller';

export default class RecoverController extends Controller {
  queryParams = ['key'];
  key = null;
}
