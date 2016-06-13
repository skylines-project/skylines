function geographicDistance(loc1_deg, loc2_deg) {
  var radius = 6367009;

  var loc1 = [loc1_deg[0] * Math.PI / 180, loc1_deg[1] * Math.PI / 180];
  var loc2 = [loc2_deg[0] * Math.PI / 180, loc2_deg[1] * Math.PI / 180];

  var dlon = loc2[0] - loc1[0];
  var dlat = loc2[1] - loc1[1];

  var a = Math.pow(Math.sin(dlat / 2), 2) +
          Math.cos(loc1[1]) * Math.cos(loc2[1]) *
          Math.pow(Math.sin(dlon / 2), 2);
  var c = 2 * Math.asin(Math.sqrt(a));

  return radius * c;
}
