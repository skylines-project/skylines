function pad(number) {
  if (number < 10) {
    return '0' + number;
  }
  return number;
}

export default function isoDate(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}
