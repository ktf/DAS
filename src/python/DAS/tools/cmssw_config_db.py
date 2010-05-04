#!/usr/bin/env python

# python modules
import os
import sys
import fnmatch
from optparse import OptionParser
try:
    # with python 2.5
    import hashlib
except:
    # prior python 2.5
    import md5

# pymongo modules
from pymongo.connection import Connection
from pymongo import DESCENDING

class RelOptionParser: 
    """
    Option parser
    """
    def __init__(self):
        self.parser = OptionParser()
        self.parser.add_option("-v", "--verbose", action="store", 
                    type="int", default=None, dest="verbose",
             help="verbose output")
        self.parser.add_option("--release", action="store", type="string", 
                                          default=False, dest="release",
             help="specify CMSSW release name")
        self.parser.add_option("--host", action="store", type="string", 
             default="localhost", dest="host",
             help="specify MongoDB hostname")
        self.parser.add_option("--port", action="store", type="string", 
             default=27017, dest="port",
             help="specify MongoDB port number")
    def getOpt(self):
        """
        Returns parse list of options
        """
        return self.parser.parse_args()


def genkey(query):
    """
    Generate a new key-hash for a given query. We use md5 hash for the
    query and key is just hex representation of this hash.
    """
    try:
        keyhash = hashlib.md5()
    except:
        # prior python 2.5
        keyhash = md5.new()

    keyhash.update(query)
    return keyhash.hexdigest()

def gen_find(filepat, top):
    for path, dirlist, filelist in os.walk(top, followlinks=True):
        for name in fnmatch.filter(filelist, filepat):
            yield os.path.join(path,name)

def connect(host, port):
    """
    Connect to MongoDB database.
    """
    connection = Connection("localhost", 27017)
    db = connection.configdb
    return db

def inject(host, port, release, debug=0):
    db = connect(host, port)
    collection = db[release]
    if  not os.environ.has_key('CMS_PATH'):
        msg = 'CMS_PATH environment is not set'
        raise Exception(msg)
    if  not os.environ.has_key('SCRAM_ARCH'):
        msg = 'SCRAM_ARCH environment is not set'
        raise Exception(msg)

    cdir = os.path.join(os.environ['CMS_PATH'], os.environ['SCRAM_ARCH'])
    cdir = os.path.join(cdir, 'cms')
    cdir = os.path.join(cdir, 'cmssw')
    cdir = os.path.join(cdir, release)
    cdir = os.path.join(cdir, 'python')
    os.chdir(cdir)

    for name in gen_find("*.py", "./"):
        if  name.find('__init__.py') != -1:
            continue
        if  debug:
            print name
        try:
            dot, system, subsystem, config = name.split('/')
        except:
            continue
        fdsc = open(name, 'r')
        content = fdsc.read()
        fdsc.close()
        record  = dict(system=system, subsystem=subsystem, 
                        config=config, content=content, hash=genkey(content))
        collection.insert(record)
        lkeys = ['system', 'subsystem', 'config', 'hash']
        index_list = [(key, DESCENDING) for key in lkeys]
        collection.ensure_index(index_list)
#
# MAIN
#
if __name__ == '__main__':

    if sys.version_info < (2, 6):
        raise Exception("This script requires python 2.6 or greater")

    optManager  = RelOptionParser()
    (opts, args) = optManager.getOpt()
    if  not opts.release:
        mgs = "Usage: find_configs.py --release <CMSSW_X_Y_Z>"
        print msg
        sys.exit(1)
    inject(opts.host, opts.port, opts.release, opts.verbose)