function pad(number) {
  if (number < 10) {
    return '0' + number;
  }
  return number;
}

export default function addDays(date, days=0) {
  var result = new Date(date);
  result.setDate(result.getDate() + days);
  return `${result.getFullYear()}-${pad(result.getMonth() + 1)}-${pad(result.getDate())}`;
}
