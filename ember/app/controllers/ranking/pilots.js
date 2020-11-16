import Controller from '@ember/controller';

export default class PilotsController extends Controller {
  queryParams = ['page'];
  page = 1;
}
