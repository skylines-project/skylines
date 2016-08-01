const RADIUS = 6367009;
const DEG_TO_RAD = Math.PI / 180;

export default function(loc1_deg, loc2_deg) {
  let loc1 = [loc1_deg[0] * DEG_TO_RAD, loc1_deg[1] * DEG_TO_RAD];
  let loc2 = [loc2_deg[0] * DEG_TO_RAD, loc2_deg[1] * DEG_TO_RAD];

  let dlon = loc2[0] - loc1[0];
  let dlat = loc2[1] - loc1[1];

  let a = Math.pow(Math.sin(dlat / 2), 2) + Math.cos(loc1[1]) * Math.cos(loc2[1]) * Math.pow(Math.sin(dlon / 2), 2);

  let c = 2 * Math.asin(Math.sqrt(a));

  return RADIUS * c;
}
