import isoDate from './iso-date';

export default function addDays(date, days = 0) {
  let result = new Date(date);
  result.setDate(result.getDate() + days);
  return isoDate(result);
}
