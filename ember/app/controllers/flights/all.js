import Controller from '@ember/controller';

export default class AllController extends Controller {
  queryParams = ['page', 'column', 'order'];
  page = 1;
  column = 'date';
  order = 'desc';
}
