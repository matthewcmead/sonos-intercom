Super low effort Sonos Intercomm.  Zero security.  Pair with an Apple Shortcut like so:

Record Audio:
  Audio Quality-> Normal
  Start Recording-> On Tap
  Finish Recording-> On Tap

->

Encode:
  Recorded Audio
  Audio Only-> ON
  Format-> AIFF

->

Get contents of:
  http://<intercommhost>:<intercommport>/sonosplay
  Method-> POST
  Request Body-> File
  File-> Encoded Media
