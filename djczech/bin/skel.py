# -*- coding: utf-8 -*-
import os, sys

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_current/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djczech.settings")

from django.conf import settings

from optparse import OptionParser

"""
Shell script...
"""

# set up command-line options
desc = """
Accepts as input...
"""

parser = OptionParser(description=desc)
parser.add_option(
    "-x", "--equis",
    help="Lorem ipsum dolor sit amet.",
    dest="equis"
)

def main():
    """
    main method
    """

######################
# shell command line
######################

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    equis = options.equis

    mandatories = ['equis',]
    for m in mandatories:
        if not options.__dict__[m]:
            print "mandatory option is missing: %s\n" % m
            parser.print_help()
            exit(-1)

    sys.exit(main())
