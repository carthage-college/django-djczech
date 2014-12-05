# -*- coding: utf-8 -*-
import os, sys

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djczech.settings")

from django.conf import settings

from optparse import OptionParser

"""
Shell script that munges CSV data
"""

import csv

# set up command-line options
desc = """
Accepts as input a file name
"""

parser = OptionParser(description=desc)
parser.add_option(
    "-f", "--file",
    help="File name.",
    dest="file"
)

def main():
    """
    main function
    """

    csvfile = open(phile, 'r')
    fieldnames = (
        "jbaccount","jbchkno","Null","jbamount","jbissue_date",
        "jbpostd_dat","jbstatus","jbstatus_date","jbpayee"
    )

    reader = csv.DictReader( csvfile, fieldnames)
    for r in reader:
        print r["jbchkno"]

######################
# shell command line
######################

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    phile = options.file

    mandatories = ['file',]
    for m in mandatories:
        if not options.__dict__[m]:
            print "mandatory option is missing: %s\n" % m
            parser.print_help()
            exit(-1)

    sys.exit(main())
