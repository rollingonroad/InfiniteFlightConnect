# 0.0.6 Todo list
- fix pylint warning done
- two issue: when IF into MainManu, it will stop response getflightplan, we need enhance recieve() to deal with diferent situation. timeout/disconnect. fixed/just settimeout and raise socket.err when get connection reset unexpect and hang.
- add IndicatedAirspeedKts, to get_aircraft_state