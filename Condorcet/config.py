"""Condorcet voting configuration.

TITLE is the title shown for the poll to the voter.
OPTIONS are the available choices shown to the voter.
AUTHORS_LIST is the name of the xml file with author lis
"""
import os

# Poll title
TITLE = 'Order the quarks in the order you prefer them'
# Poll options
OPTIONS = ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Beauty']
# Contact email address
CONTACT = 'admin@example.com'

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

# xml file with author list, can be downloaded form:
# https://lhcbglance.web.cern.ch/lhcbglance/membership/authorlist.php
# write only the file name and place the file in the same folder as this config file

AUTHORS_LIST = 'LHCb_Authorship_flat_28-Mar-2015.xml'

# Key for encypting session information
SECRET_KEY = 'cH\xc5\xd9\xd2\xc4,^\x8c\x9f3S\x94Y\xe5\xc7!\x06>A'

# SQLite3 database paths
SQLALCHEMY_DATABASE_URI = r'sqlite:///databases/votes.db'
SQLALCHEMY_BINDS = {
    'voters': r'sqlite:///databases/voters.db',
}
