# Import modules
import json
import os
import pprint
import random
import shlex
import subprocess
import sys


# Functions

def create_pass_entry(metadata):
    """Create a pass entry

    Creates a pass entry from supplied info.

    Metadata is a dict with any metadata. Basic info should contain, in this order:
        Password
        Username (used to log in to web site)
        URL(s)
        Email (if different from username)
        Username

    Args:
        name: Full/Path/To/Entry
        metadata: Dict with additional info as descrived above
    
    Returns:
        Null if successful, or error if not
    """

    title = metadata['name']
    if not title:
        return None
    
    while os.path.isfile(f'/home/twilight/.password-store/{title}.gpg'):
        title += '_' + metadata['username']

    out = ''

    if metadata.get('password'):
        out += metadata.get('password') + '\n'

    for key, value in metadata.items():
        if not key == 'name' and not key == 'password':
            out += key + ': ' + str(value) + '\n'

    subprocess.run(f"echo {shlex.quote(out)} | pass insert -m '{title}'", shell=True)


def import_1pif(path):
    """Import 1pif file

    Args:
        path: /full/path/to/data.1pif

    Returns:
        List of file contents or none if error
    """

    # Check if the file exist
    if not os.path.isfile(path):
        return None

    # Else load the file
    f = open(path, 'r')
    temp = [line for line in f]
    f.close()

    lines = []
    for x in temp:
        if not x.startswith('***'):
            lines.append(x.strip())
    


    return(lines)


def decode_1pif_entry(string):
    """Get all data from 1pif entry

    Args:
        A single json string entry from data.1pif
    
    Returns:
        Dict of all the data
    """

    json_string = json.loads(string)
    data = {}
    data['name'] = ''

    if json_string['typeName'] == 'webforms.WebForm' and not json_string.get('trashed'):
        # Get stuff
        tags = json_string.get('openContents', {}).get('tags')
        if tags:
            tags = tags[0].replace(' ', '_')
            data['name'] += tags
        
        if data['name']:
            data['name'] += '/'

        name = json_string.get('title')
        if name:
            name = name.replace(' ', '_').replace('/', '_')
            data['name'] += name
        
        secureContents = json_string.get('secureContents', {})
        if secureContents:
            secureContents_fields = secureContents.get('fields', [])
            for field in secureContents_fields:
                try:
                    key = str(field['name']).replace(' ', '_')
                except KeyError:
                    continue
                count = 1
                while key in data:
                    count += 1
                    key += '_' + str(count)
                try:
                    data[key] = field['value']
                except KeyError as e:
                    print(e, '\n', string)
                    exit(1)

            urls = secureContents.get('URLs', [])
            for url in urls:
                key = 'URL'
                count = 1
                while key in data:
                    count += 1
                    key += '_' + str(count)
                try:
                    data[key] = url['url']
                except KeyError:
                    continue

            secureContents_section = secureContents.get('sections', [])
            for section in secureContents_section:
                fields = section.get('fields', [])
                for field in fields:
                    key = str(field['t']).replace(' ', '_')
                    count = 1
                    while key in data:
                        count += 1
                        key += '_' + str(count)
                    try:
                        data[key] = field['v']
                    except KeyError:
                        pass
            
            note = secureContents.get('notesPlain')
            if note:
                data['note'] = note
    
    return data

if __name__ == "__main__":
    # Get input file
    try:
        pif_file_path = str(sys.argv[1])
    except IndexError:
        print('One input file must be specified. Example:\npython3 /path/to/data.1pif')
        exit(1)
    
    pif_contents = import_1pif(pif_file_path)
    if pif_contents:
        random.shuffle(pif_contents)
        for line in pif_contents:
            data = decode_1pif_entry(line)
            if data:
                create_pass_entry(data)

