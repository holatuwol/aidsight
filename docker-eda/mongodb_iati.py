from __future__ import print_function

from datetime import datetime
import io
import json
import os
import pymongo
import xmltodict

conn = pymongo.MongoClient('mongodb', 27017)
db = conn.iati

activity_failures = {}
activity_xml_failures = {}

db.drop_collection('activities')
db.drop_collection('activities_metadata')
db.drop_collection('transactions')

activities = db.activities
activities_metadata = db.activities_metadata
transactions = db.transactions

with io.open('activities_metadata.json', 'r', encoding = 'utf8') as f:
    activity_metadata_json = json.load(f)
    activity_metadata_dict = { item['name']: item for item in activity_metadata_json }

def insert_activity(entries, f, metadata_key, generated_datetime):
    if type(entries) != list:
        entries = [entries]

    activity_transactions = []

    for entry in entries:
        if 'transaction' in entry:
            entry_transactions = entry['transaction']

            if type(entry_transactions) != list:
                entry_transactions = [entry_transactions]

            for transaction in entry_transactions:
                if 'iati-identifier' in entry:
                    transaction['@w210-activity'] = entry['iati-identifier']

                transaction[u'@w210-key'] = metadata_key
                transaction[u'@generated-datetime'] = generated_datetime

            activity_transactions += entry_transactions

        entry[u'@w210-key'] = metadata_key
        entry[u'@generated-datetime'] = generated_datetime

    if len(entries) > 0:
        activities.insert_many(entries)

    if len(activity_transactions) > 0:
        transactions.insert_many(activity_transactions)

def insert_activities(f, i):
    # Extract the activities, but store the remainder as metadata we
    # can join with for other purposes.

    if 'iati-activity' not in i['iati-activities']:
        return

    entries = i['iati-activities']['iati-activity']
    del i['iati-activities']['iati-activity']

    metadata_key = f.name[5:-4]

    if metadata_key in activity_metadata_dict:
        i.update(activity_metadata_dict[metadata_key])

    # Save this alongside each entry

    i['@w210-key'] = metadata_key

    activities_metadata.insert_one(i)

    generated_datetime = None

    if '@generated-datetime' in i['iati-activities']:
        generated_datetime = i['iati-activities']['@generated-datetime']

    insert_activity(entries, f, metadata_key, generated_datetime)

def import_activity_xml(f, xml):
    try:
        i = xmltodict.parse(xml)
    except Exception as e:
        activity_xml_failures[f.name] = e
        return

    # Check for errors in activity structure

    try:
        insert_activities(f, i)
    except Exception as e:
        activity_failures[f.name] = e

def import_activity_document(f):
    global activity_failures, activity_xml_failures

    xml=f.read()

    if xml.find('iati-activities') == -1:
        activity_xml_failures[f.name] = 'html'
        return

    import_activity_xml(f, xml)

organization_failures = {}
organization_xml_failures = {}

db.drop_collection('organizations')
db.drop_collection('organizations_metadata')

organizations = db.organizations
organizations_metadata = db.organizations_metadata

with io.open('organization_metadata.json', 'r', encoding = 'utf8') as f:
    organization_metadata_json = json.load(f)
    organization_metadata_dict = { item['name']: item for item in organization_metadata_json }

def import_organization_xml(f, xml):
    i = xmltodict.parse(xml)

    # Extract the organizations, but store the remainder as metadata we
    # can join with for other purposes.

    entries = i['iati-organisations']['iati-organisation']
    del i['iati-organisations']['iati-organisation']

    metadata_key = f.name[10:-4]

    if metadata_key in organization_metadata_dict:
        i.update(organization_metadata_dict[metadata_key])

    # Save this alongside each entry

    i['@w210-key'] = metadata_key

    organizations_metadata.insert_one(i)

    generated_datetime = None

    if '@generated-datetime' in i['iati-organisations']:
        generated_datetime = i['iati-organisations']['@generated-datetime']

    if type(entries) != list:
        entries = [entries]

    for entry in entries:
        entry['@w210-key'] = metadata_key
        entry['@generated-datetime'] = generated_datetime

    organizations.insert_many(entries)

def import_organization_document(f):
    global organization_failures, organization_xml_failures

    # The XML file may be encoded as UTF-16 or really any other encoding.
    # If it doesn't contain the "<iati-activities" tag, then it may be
    # due to an encoding problem.

    xml=f.read()

    if xml.find('iati-organisations') == -1:
        if xml.find('iati-activities') != -1:
            organization_xml_failures[f.name] = 'activities'
            return

        organization_xml_failures[f.name] = 'html'
        return

    try:
        import_organization_xml(f, xml)
        return
    except Exception as e:
        organization_xml_failures[f.name] = e