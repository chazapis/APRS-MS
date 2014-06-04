def doHash(callsign):
    # Based on the doHash function found in most APRS software.
    # The following copyright notice is copied in verbatim.
    
    # Note: The doHash(char*) function is Copyright Steve Dimse 1998
    # As of April 11 2000 Steve Dimse has released this code to the open source APRS community
    
    # Remove SSID, trim callsign, and convert to upper case.
    cuthere = callsign.find("-")
    if (cuthere != -1):
        callsign = callsign[:cuthere]
    realcall = callsign[:10].upper()
    
    if (realcall == "NOCALL"):
        return "-1"
    
    # Initialize hash.
    hash = 0x73e2
    i = 0
    length = len(realcall)
    
    # Hash callsign two bytes at a time.
    while (i < length):
        hash ^= ord(realcall[i])<<8
        if (i+1 < length):
            hash ^= ord(realcall[i+1])
        i += 2
    
    # Convert to string and mask off the high bit so the number is always positive.
    return str(hash & 0x7fff)
