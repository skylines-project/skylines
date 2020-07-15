import Controller from '@ember/controller';

export default class DateController extends Controller {
  queryParams = ['page', 'column', 'order'];
  page = 1;
  column = 'score';
  order = 'desc';
}
