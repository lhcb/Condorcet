"""Condorcet voting configuration.

TITLE is the title shown for the poll to the voter.
OPTIONS are the available choices shown to the voter.
AUTHORS_LIST is the name of the xml file with author lis
"""
import os
import sys
this_files_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(this_files_dir, '..'))

# Poll title
TITLE = 'Order the quarks in the order you prefer them'
# Poll options
OPTIONS = ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Beauty']
# Contact email address
CONTACT = 'admin@example.com'

# Dates

# Format to parse the date, see details at https://docs.python.org/2/library/time.html#time.strftime
DATE_FORMAT = '%d/%m/%Y %H.%M' # '%d/%m/%Y'
# Startig time of the election
START_ELECTION = '28/03/2008 12.23'
# Closing time of the election
CLOSE_ELECTION = '28/03/2029 12.47'
# Time from when it is possible to see the results
VIEW_RESULTS = '28/03/2014 12.24'


# xml file with author list, can be downloaded form: https://lhcbglance.web.cern.ch/lhcbglance/membership/authorlist.php
# write only the file name and place the file in the same folder as this config file
AUTHORS_LIST = 'LHCb_Authorship_flat_28-Mar-2015.xml'

####################################################################################################

# Configuration below is for the application itself, does not affect voting

# Run the application in debug mode?
# Set to True if the DEBUG environment variable is set (to anything)
try:
    _ = os.environ['DEBUG']
    DEBUG = True
except KeyError:
    DEBUG = False

# Root path the site lives at
APPLICATION_ROOT = '/' if DEBUG else '/gdujany/Condorcet'

# Key for encypting session information
SECRET_KEY = 'cH\xc5\xd9\xd2\xc4,^\x8c\x9f3S\x94Y\xe5\xc7!\x06>A'

# SQLite3 database paths
# Name of the folder to contain the databases
DB_DIR = os.path.join(this_files_dir, 'databases')
# Name of the database file to hold votes
VOTES_DB = 'votes.db'
# Name the database file to hold list of voters who have voted
VOTERS_DB = 'voters.db'
SQLALCHEMY_DATABASE_URI = r'sqlite:///{0}/{1}'.format(DB_DIR, VOTES_DB)
SQLALCHEMY_BINDS = {
    'voters': r'sqlite:///{0}/{1}'.format(DB_DIR, VOTERS_DB),
}
