from __future__ import print_function

import chardet
from datetime import datetime
import functools
import io
from multiprocessing import cpu_count, Pool
import os
import requests
import sys

try:
    unicode = str
except:
    pass

def download_all(folder, metadata_resources):
    items = [
        (short_name, resource_urls)
            for short_name, resource_urls in metadata_resources.items()
                if not os.path.isfile(folder + '/' + short_name + '.xml')
    ]

    pool = Pool(cpu_count())

    print('%s Downloaded %d of %d' % (datetime.now(), 0, len(items)))

    num_finished = 0

    for result in pool.imap_unordered(functools.partial(download_one_file, folder), items):
        num_finished += 1

        if num_finished % 100 == 0:
            print('%s Downloaded %d of %d' % (datetime.now(), num_finished, len(items)))

    pool.close()

def download_one(folder, short_name, resource_urls):
    iati_filename = folder + '/' + short_name + '.xml'

    if os.path.isfile(iati_filename):
        return False

    for resource_url in resource_urls:
        r = None

        try:
            r = requests.get(resource_url, timeout=10)
        except:
            continue

        if r is None or r.status_code != 200:
            continue

        if reencode_one(iati_filename, r.content):
            return True

    return False

def download_one_file(folder, item):
    short_name, resource_urls = item
    return download_one(folder, short_name, resource_urls)

def generate_script(folder, metadata_titles, metadata_resources):
    download_lines = [
        '%s\tiati/%s.xml' % (resource_urls[0], short_name)
            for short_name, resource_urls in metadata_resources.items()
                if not os.path.isfile('iati/%s.xml' % short_name)
    ]

    with open('download_iati.txt', 'w', encoding='utf-8') as csv_file:
        csv_file.write('\n'.join(download_lines))

    script_lines = [
        '#!/bin/bash',
        'mkdir -p %s' % folder,
        'SHELL=/bin/sh parallel -a download_iati.txt --colsep "\\t" -P %d curl -Ls -f -k -o "{2}" --connect-timeout 10 "{1}"' % cpu_count()
    ]

    with io.open('download_iati.sh', 'w', encoding='utf-8') as script_file:
        script_file.write('\n'.join(script_lines))

def reencode_all(folder, metadata_resources):
    keys = [
        short_name
            for short_name in metadata_resources.keys()
                if os.path.isfile(folder + '/' + short_name + '.xml')
    ]

    pool = Pool(cpu_count())

    print('%s Re-encoded %d of %d' % (datetime.now(), 0, len(keys)))

    num_finished = 0

    for result in pool.imap_unordered(functools.partial(reencode_one_file, folder), keys):
        num_finished += 1

        if num_finished % 100 == 0:
            print('%s Re-encoded %d of %d' % (datetime.now(), num_finished, len(keys)))

    pool.close()

def reencode_one(iati_filename, xml):
    charset = chardet.detect(xml)

    if charset is None or charset['encoding'] is None:
        print('failed to detect character encoding for %s' % iati_filename)
        return False

    try:
        xml = xml.decode(charset['encoding'])
    except:
        print('failed to decode %s with encoding %s' % (iati_filename, charset['encoding']))
        return False

    # Change the encoding declaration

    if xml[0:5] == '<?xml':
        xml = '<?xml version="1.0" encoding="UTF-8"?>' + xml[xml.find('>')+1:]

    with io.open(iati_filename, 'w', encoding = 'utf-8') as outfile:
        outfile.write(unicode(xml))

    return True

def reencode_one_file(folder, short_name):
    iati_filename = folder + '/' + short_name + '.xml'

    if not os.path.isfile(iati_filename):
        return False

    with io.open(iati_filename, 'rb') as infile:
        xml = infile.read()

    return reencode_one(iati_filename, xml)

if __name__ == '__main__':
    download_one(sys.argv[1], sys.argv[2], sys.argv[3:])