function pad(number) {
  return number < 10 ? `0${number}` : number;
}

export default function isoDate(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}
