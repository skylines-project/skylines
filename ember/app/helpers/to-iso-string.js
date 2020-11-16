import { helper } from '@ember/component/helper';

export default helper(([date]) => new Date(date).toISOString());
