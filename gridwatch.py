#!/usr/bin/python

import sys
import urllib

import requests
import xmltodict
import json

try:
    from argparse import ArgumentParser as ArgParser
except ImportError:
    from optparse import OptionParser as ArgParser

def get_xml(uri):
    xml = requests.get(uri).content
    return xmltodict.parse(xml)

def get_data():
    base_uri = 'http://www.bmreports.com/bsp/additional/soapfunctions.php?'

    generation = get_xml(base_uri + 'element=generationbyfueltypetable&submit=Invoke')['GENERATION_BY_FUEL_TYPE_TABLE']['INST']
    frequency = get_xml(base_uri + 'output=XML&element=rollingfrequency&submit=Invoke')['ROLLING_SYSTEM_FREQUENCY']
    demand = get_xml(base_uri + 'output=XML&element=rollingdemand&submit=Invoke')['ROLLING_DEMAND']

    nationalgrid = {}
    nationalgrid['DateTime'] = generation['@AT']
    nationalgrid['TotalGeneration'] = int(generation['@TOTAL'])
    nationalgrid['Frequency'] = float(frequency['ST'][-1]['@VAL'])
    nationalgrid['SystemDemand'] = int(demand['ST'][-1]['@VAL'])

    nationalgrid['GenerationByType'] = {}
    nationalgrid['Interconnects'] = {}

    for fuel in generation['FUEL']:
        type = fuel['@TYPE']
        if fuel['@IC'] == 'N':
            nationalgrid['GenerationByType'][type] = int(fuel['@VAL'])
        else:
            nationalgrid['Interconnects'][type] = int(fuel['@VAL'])

    return nationalgrid

def main(argv):

    parser = ArgParser()
    # Give optparse.OptionParser an `add_argument` method for
    # compatibility with argparse.ArgumentParser
    try:
        parser.add_argument = parser.add_option
    except AttributeError:
        pass
    parser.add_argument('--jsonuri', help='Specify a URI to post the json output to')

    options = parser.parse_args()
    if isinstance(options, tuple):
        args = options[0]
    else:
        args = options
    del options

    grid_status = get_data()

    if args.jsonuri:
        req = urllib.request.Request(url=args.jsonuri, data=json.dumps(grid_status).encode('utf8'), method='POST')
        req.add_header('Content-Type', 'application/json')
        try:
            with urllib.request.urlopen(req) as f:
                pass
        except:
            print('Could not submit results to ' + args.jsonuri)

    else:
        print(json.dumps(grid_status, sort_keys=True))

if __name__ == "__main__":
   main(sys.argv[1:])