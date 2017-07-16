import geocoder
import itertools
import json
import re
import requests
import six

publisher_nodes = {}
organization_nodes = {}
activity_nodes = {}
activity_relationships = {}

def get_text(item):
    if type(item) == dict:
        if '#text' in item:
            return get_text(item['#text'])
        elif 'narrative' in item:
            if type(item['narrative']) != list:
                return get_text(item['narrative'])

    if isinstance(item, six.string_types):
        return item
    else:
        return ''

def remove_list(activity, attribute):
    if attribute not in activity:
        return []

    value = activity[attribute]
    del activity[attribute]

    if type(value) != list:
        value = [value]

    return value

def replace_list(activity, key, attribute):
    item_list = remove_list(activity, key)

    if item_list is None or len(item_list) == 0:
        return

    value = [
        item[attribute]
            for item in item_list
                if item is not None and attribute in item and item[attribute] != ''
    ]

    if len(value) > 0:
        activity[key] = value

# Based off of the following StackOverflow post for flattening dictionaries
# http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys

def flatten(d, parent_key=None):
    items = []

    for k, v in d.items():
        new_key = parent_key + '_' + k if parent_key is not None else k

        new_key = new_key.replace('@', '')
        new_key = new_key.replace('#', '')
        new_key = new_key.replace(':', '')
        new_key = new_key.replace('-', '_')

        if type(v) == dict:
            items.extend(flatten(v, new_key))
        elif type(v) == list:
            sub_items = [get_text(item) for item in v]
            items.append((new_key, sub_items))
        else:
            items.append((new_key, v))

    return items

geocoder_cache = {}

def get_location(location, activity_id):
    global geocoder_cache
    
    failed_parse = None
    
    if 'point' in location:
        point = location['point']

        if point is not None and 'pos' in point:
            pos = point['pos']

            if pos is not None and pos != '' and pos != '0':
                try:
                    if pos.find(' ') == -1 and pos.find(',') == -1:
                        failed_parse = pos
                        pos = None
                    elif pos.find(' ') == -1:
                        pos = tuple([float(x) for x in point['pos'].strip().split(',')])
                    else:
                        pos = tuple([float(x.replace(',', '.')) for x in re.split('\s+', point['pos'].strip())])
                except:
                    failed_parse = point['pos']
                    pos = None

            if pos is not None and pos != '' and pos != '0':
                try:
                    if pos in geocoder_cache:
                        lookup = geocoder_cache[pos]
                    else:
                        lookup = geocoder.google(pos, method = 'reverse')
                        geocoder_cache[pos] = lookup

                    return lookup.address
                except:
                    failed_parse = point['pos']
                    pass

    if 'name' in location:
        location_name = get_text(location['name'])

        if location_name is not None:
            return location_name

    if failed_parse is not None:
        print('failed to parse %s for activity %s' % (failed_parse, activity_id))

    return None

def get_activity_location(activity):
    if 'location' not in activity:
        return None

    activity_id = activity['iati-identifier']
    location = activity['location']

    if location is None:
        return None

    if type(location) == list:
        activity_location = [get_location(item, activity_id) for item in location]
    else:
        activity_location = [get_location(location, activity_id)]

    return activity_location

# Extract country

country_url = 'http://iatistandard.org/202/codelists/downloads/clv3/json/en/Country.json'
countries_json = requests.get(country_url).json()
countries = { item['code']: item['name'] for item in countries_json['data'] }

def get_recipient_country(activity):
    location_name = []

    if 'recipient-country' in activity:
        country = activity['recipient-country']

        if '@code' in country:
            code = country['@code']

            if code in countries:
                return countries[code]

    return None

# Extract sector

def get_sectors(activity):
    if 'sector' not in activity:
        return []

    sectors = activity['sector']

    if type(sectors) == dict:
        sectors = [sectors]

    return [sector['@code'] for sector in sectors if '@code' in sector]

# Parse organization information

def is_valid_ref_format(ref):
    if ref.find('-') == -1:
        return False

    if ref.find(' ') != -1:
        return False

    return True

def add_organization(organization):
    global organization_nodes

    if '@ref' not in organization:
        return None

    organization_ref = organization['@ref']

    if organization_ref not in organization_nodes:
        if not is_valid_ref_format(organization_ref):
            return None

        organization_node = {'ref': organization_ref}

        organization_nodes[organization_ref] = organization_node
    else:
        organization_node = organization_nodes[organization_ref]

    return organization_node

# Activity edges

activity_fields = set([
    'iati-identifier',
    'description',
    'reporting-org',
    'participating-org',
    'recipient-country',
    'location',
    'policy-marker',
    'sector'
])

def add_activity_node(activity):
    global activity_fields, activity_nodes

    if 'iati-identifier' not in activity:
        return

    activity = {
        key : value for key, value in activity.items()
            if key in activity_fields
    }

    activity_key = activity['iati-identifier']

    if activity_key in activity_nodes:
        return

    reporters = remove_list(activity, 'reporting-org')
    participants = remove_list(activity, 'participating-org')

    replace_list(activity, 'activity-date', '@iso-date')
    replace_list(activity, 'sector', '@code')
    replace_list(activity, 'policy-marker', '@code')

    recipient_country = get_recipient_country(activity)

    if recipient_country is None:
        if 'recipient-country' in activity:
            del activity['recipient-country']
    else:
        activity['recipient-country'] = recipient_country

    location = get_activity_location(activity)

    if location is None:
        if 'location' in activity:
            del activity['location']
    else:
        activity['location'] = location

    if 'description' in activity:
        description_text = get_text(activity['description']).strip().lower()

        tokenized_text = set([
            item for item in re.split('[^a-z]+', description_text.strip().lower())
                if len(item) > 0
        ])

        activity['description'] = tokenized_text
        activity['description_raw'] = description_text

    else:
        activity['description'] = set()
        activity['description_raw'] = ''

    try:
        relationships = []

        activity_node = activity
        activity_nodes[activity_key] = activity_node

        for reporter, participant in itertools.product(reporters, participants):
            add_activity_relationship(activity_key, relationships, reporter, reporter)
            add_activity_relationship(activity_key, relationships, reporter, participant)

        activity_relationships[activity_key] = relationships
    except Exception as e:
        print(json.dumps(activity, indent=2))
        raise e

def add_activity_relationship(activity_key, relationships, reporter, participant):
    global publisher_nodes

    reporter_node = add_organization(reporter)
    participant_node = add_organization(participant)

    if reporter_node is None or participant_node is None:
        return

    if reporter_node['ref'] not in publisher_nodes:
        publisher_nodes[reporter_node['ref']] = reporter_node

    has_relationship = False

    for relationship in relationships:
        if relationship['start'] == reporter_node['ref'] and relationship['end'] == participant_node['ref']:
            has_relationship = True
            break

    if not has_relationship:
        ref_edge = {
            'start': reporter_node['ref'],
            'activity': activity_key,
            'end': participant_node['ref']
        }

        relationships.append(ref_edge)