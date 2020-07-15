import Controller from '@ember/controller';

export default class ClubsController extends Controller {
  queryParams = ['page'];
  page = 1;
}
