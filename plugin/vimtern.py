#!/usr/bin/env python
'''
VIMTern.py dispatch work to your intern via Slack from the command line.
'''
from random import randint
from sys import exit, argv
import argparse
import json
import yaml  # To load the intrn file

VERBOSE = False

try:
    import requests
except ImportError:
    print "Unable to import requests. Run `pip install requests`."
    exit(1)


def _load_intrn(intrn_file="default.intrn"):
    '''
    Load the config file.
    '''
    config = None
    with open(intrn_file, 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as ex:
            print str(ex)
            exit(1)
    return config


def vimtern_do(msg, intrn_file):
    '''
    Issue commands to 1ntern.
    '''
    global VERBOSE
    if not intrn_file:
        raise AttributeError("Path to .intrn file required.")
    config = _load_intrn(intrn_file)
    if not msg or msg == '':
        num = len(config["default_msgs"])
        msg = config["default_msgs"][randint(0, num - 1)]
    if not isinstance(msg, basestring):
        print "vimtern_do: msg is not a string."
        print "msg: ", msg
        exit(1)

    # Build JSON message payload
    msg = msg.replace('"', '').strip()
    channel = config["Slack"]["channel"]
    username = config["Slack"]["username"]
    icon_emoji = config["Slack"]["icon_emoji"]
    payload = json.dumps({
        "text": msg,
        "channel": channel,
        "username": username,
        "icon_emoji": icon_emoji,
        "parse": "full"
    })

    # Create and send POST request to Slack webhook
    slack_uri = config['Slack']['uri']
    try:
        r = requests.post(slack_uri, data=payload, headers={
                          'Content-type': 'application/json'})
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        print "Could not establish connection to Slack."
        exit(1)
    except requests.exceptions.HTTPError as err:
        print "Slack API request was not successful."
        print err.message
        exit(1)
    except requests.exceptions.Timeout:
        print "Slack API request timed out."
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f",
                        "--config",
                        dest='config',
                        help="Path to the .intrn config file.")
    parser.add_argument("-m",
                        "--msg",
                        dest='msg',
                        help="Message to send.",
                        default="")
    parser.add_argument('-v',
                        '--verbose',
                        dest='verbose',
                        action='store_true',
                        help='Verbose mode to help debug.')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    VERBOSE = args.verbose

    if VERBOSE:
        print "ARGS: ", argv
    try:
        vimtern_do(args.msg, args.config)
    except Exception, e:
        print str(e)
        parser.print_help()
