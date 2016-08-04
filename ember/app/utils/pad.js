export default function pad(number) {
  return number < 10 ? `0${number}` : number;
}
