{
  "iTotalDisplayRecords": ${response_dict['iTotalDisplayRecords']},
  "iTotalRecords": ${response_dict['iTotalRecords']},
  "sColumns": "${response_dict['sColumns']}",
  "sEcho": ${response_dict['sEcho']},
  "aaData": [
  % for flight in flights:
    ["${flight.takeoff_time.strftime('%x')}",
     ${flight.olc_plus_score},
     "\
       % if flight.pilot:
         <a href=\"/flights/pilot/${flight.pilot_id}\">${flight.pilot}</a>\
       % endif
       % if flight.co_pilot:
         <br /><a href=\"/flights/pilot/${flight.co_pilot_id}\">${flight.co_pilot}</a>\
       % endif
       % if not flight.pilot and not flight.co_pilot:
         [${flight.owner}]\
       % endif
     ",
     "${flight.olc_classic_distance and str(flight.olc_classic_distance/1000)} km",
     "${flight.club}",
     "${flight.takeoff_time.strftime('%H:%M') + "-" + flight.landing_time.strftime('%H:%M')}",
     "<a href=\"/flights/id/${flight.id}\">Show</a>"]\
     % if loop.last != True:
     ,
     % endif
  % endfor
]}
