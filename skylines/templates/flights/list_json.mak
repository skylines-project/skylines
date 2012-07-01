<% from babel.dates import format_date %>\
{
  "iTotalDisplayRecords": ${response_dict['iTotalDisplayRecords']},
  "iTotalRecords": ${response_dict['iTotalRecords']},
  "sColumns": "${response_dict['sColumns']}",
  "sEcho": ${response_dict['sEcho']},
  "aaData": [
  % for flight in flights:
    [
     % if not date:
     "\
       % if flight.takeoff_time:
         <span title=\"${flight.takeoff_time.strftime('%d.%m.%Y')}\">\
           ${format_date(flight.takeoff_time)}\
         </span>\
       % endif
     ",
     % endif
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
     % if not club and not pilot:
     "\
       % if flight.club:
         <a href=\"/clubs/${flight.club_id}/\">${flight.club}</a>\
       % endif
     ",
     % endif
     "${flight.takeoff_time and flight.landing_time and flight.takeoff_time.strftime('%H:%M') + "-" + flight.landing_time.strftime('%H:%M')}",
     "<a href=\"/flights/${flight.id}/\">Show</a> <a class=\"pin no-link\" style=\"visibility: hidden;\" rel=\"tooltip\" title=\"Activate this to show the flight on top of other flights on the map\">${flight.id}</span>"]\
     % if loop.last != True:
     ,
     % endif
  % endfor
]}
