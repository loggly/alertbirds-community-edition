#!/usr/bin/env python

import sys
from optparse import OptionParser

from pagerduty import PagerDuty, PagerDutyException

def build_opt_parser():
    parser = OptionParser(usage="Usage: %prog [options] <trigger/acknowledge/resolve>")
    parser.add_option("-d", "--details", dest="details", help="Optional JSON details")
    parser.add_option("", "--description", dest="description", help="Description")
    parser.add_option("-i", "--incident", dest="incident_key", help="unique incident key")
    parser.add_option("-k", "--key", dest="service_key", help="service key")
    return parser

def main():
    parser = build_opt_parser()
    (options, args) = parser.parse_args()
    if not args:
        parser.error("must specify an action: trigger, acknowledge, or resolve")
    if not options.service_key:
        parser.error("service key is required")
    
    action = args[0]
    
    description = options.description
    if action == "trigger":
        if description in (None, "-"):
            description = sys.stdin.read()
        if not description:
            sys.stderr.write("Action trigger requires a description\n")
            sys.exit(1)
    elif action in ("acknowledge", "resolve"):
        if not options.incident_key:
            sys.stderr.write("Action %s requires an incident key\n" % action)
            sys.exit(1)
        if description == "-":
            description = sys.stdin.read()
    
    pg = PagerDuty(options.service_key)
    try:
        ik = getattr(pg, action)(
            description = description,
            incident_key = options.incident_key,
            details = options.details,
        )
    except PagerDutyException, exc:
        sys.stderr.write(str(exc)+"\n")
        sys.exit(2)
    
    if ik:
        print ik

if __name__ == "__main__":
    main()
