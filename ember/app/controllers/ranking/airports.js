import Controller from '@ember/controller';

export default class AirportsController extends Controller {
  queryParams = ['page'];
  page = 1;
}
