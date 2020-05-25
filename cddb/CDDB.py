#!/usr/bin/env python3
"""
Module for retrieving CDDB v1 data from CDDB servers via HTTP

Written 17 Nov 1999 by Ben Gertzfield <che@debian.org>
This work is released under the GNU GPL, version 2 or later.

Release version 1.4
 
Change version to 0.1 due to transformation to python3
by Michael Rasmussen <mir@datanom.net>
 - Patched to work in python3
 - 'track_info' can be and instance off discid.Disc from
   python3-libdiscid
 - Add feature to use login for default_user and hostname
"""

import urllib.parse, urllib.request, os, socket, re
try:
  from libdiscid.compat import discid
except ImportError:
    import discid

name = 'CDDB.py'
version = 0.1

user = os.getenv('CDDB_EMAIL')
if user:
    (default_user, hostname) = user.split('@')
else:
    user = os.getenv('USE_SYSTEM_USER')
    if user and user.casefold() == 'true':
        default_user = os.getlogin()
        hostname = socket.getfqdn()
    else:
        default_user = 'unknown'
        hostname = 'localhost'

# Use protocol version 5 to get DYEAR and DGENRE fields.
proto = 5
default_server = 'http://freedb.freedb.org/~cddb/cddb.cgi'

def _query_libdiscid(disc_id):
    toc = disc_id.toc_string.split()[3:]
    toc.append(disc_id.seconds)
    return (disc_id.freedb_id, disc_id.last_track_num, toc)

def query(track_info, server_url=default_server,
	  user=default_user, host=hostname, client_name=name,
          client_version=version):

    if isinstance(track_info,  discid.Disc) or isinstance(track_info, discid.Disc):
        track_info = _query_libdiscid(track_info)
    
    disc_id = track_info[0]
    num_tracks = track_info[1]

    query_str = (('%s %d ') % (disc_id, num_tracks))

    for i in range(len(track_info[2])):
        query_str = query_str + ('%s ' % track_info[2][i])
	
    query_str = urllib.parse.quote_plus(query_str)

    url = "%s?cmd=cddb+query+%s&hello=%s+%s+%s+%s&proto=%i" % \
	  (server_url, query_str, user, host, client_name,
           client_version, proto)

    response = urllib.request.urlopen(url)
    
    # Four elements in response (lines splitted by \r\n): status, category, disc-id, title
    lines = response.read().decode('utf-8').split('\r\n')

    status = int(lines[0].split()[0])

    if status == 200: # OK
        result = { 'category': lines[1], 'disc_id': lines[2], 'title': lines[3] }

        return [ status, result ]

    elif status == 211 or status == 210: # multiple matches
        result = []

        for line in lines[1:]:
            if line == '.': # end of matches
                break
            match = line.split(' ', 2)

            result.append({ 'category': match[0], 'disc_id': match[1], 'title': match[2] })

        return [ status, result ]

    else:
        return [ status, None ]

def read(category, disc_id, server_url=default_server, 
	 user=default_user, host=hostname, client_name=name,
         client_version=version):

    url = "%s?cmd=cddb+read+%s+%s&hello=%s+%s+%s+%s&proto=%i" % \
	  (server_url, category, disc_id, user, host, client_name,
           client_version, proto)

    response = urllib.request.urlopen(url)
    
    lines = response.read().decode('utf-8').split('\r\n')

    status = int(lines[0].split()[0])
    
    if status == 210 or status == 417: # success or access denied
        reply = []

        for line in lines[1:]:
            if line == '.':
                break;

            reply.append(line)

        if status == 210:		
            # success, parse the reply
            return [ status, parse_read_reply(reply) ]
        else: # access denied. :(
            return [ status, reply ]
    else:
        return [ status, None ]

def parse_read_reply(comments):
    
    len_re = re.compile(r'#\s*Disc length:\s*(\d+)\s*seconds')
    revis_re = re.compile(r'#\s*Revision:\s*(\d+)')
    submit_re = re.compile(r'#\s*Submitted via:\s*(.+)')
    keyword_re = re.compile(r'([^=]+)=(.*)')

    result = {}

    for line in comments:
        keyword_match = keyword_re.match(line)
        if keyword_match:
            (keyword, data) = keyword_match.groups()
            
            if keyword in result:
                result[keyword] = result[keyword] + data
            else:
                result[keyword] = data
            continue

        len_match = len_re.match(line)
        if len_match:
            result['disc_len'] = int(len_match.group(1))
            continue

        revis_match = revis_re.match(line)
        if revis_match:
            result['revision'] = int(revis_match.group(1))
            continue

        submit_match = submit_re.match(line)
        if submit_match:
            result['submitted_via'] = submit_match.group(1)
            continue

    return result
