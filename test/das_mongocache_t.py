#!/usr/bin/env python
#pylint: disable-msg=C0301,C0103

"""
Unit test for DAS mongocache class
"""

import os
import time
import unittest

from pymongo.connection import Connection

from DAS.utils.das_config import das_readconfig
from DAS.utils.logger import DASLogger
from DAS.core.das_mongocache import DASMongocache
from DAS.core.das_mongocache import update_item

class testDASMongocache(unittest.TestCase):
    """
    A test class for the DAS mongocache class
    """
    def setUp(self):
        """
        set up DAS core module
        """
        debug    = 0
        config   = das_readconfig()
        logger   = DASLogger(verbose=debug, stdout=debug)
        config['logger']  = logger
        config['verbose'] = debug

        connection = Connection("localhost", 27017)
        connection.drop_database('das') 
        self.dasmongocache = DASMongocache(config)

    def test_update_item(self):
        """test update_item method"""
        expect = {'test':1, 'block' : {'name' : '/a/b/c#123'}}

        row = {'test':1}
        key = 'block.name'
        val = '/a/b/c#123'
        update_item(row, key, val)
        self.assertEqual(expect, row)

        row = {'test':1}
        key = 'block.name'
        val = {'$gte' : '/a/b/c#123'}
        update_item(row, key, val)
        # upon update we create a list of values for given key: block.name
        expect = {'test':1, 'block' : {'name' : ['/a/b/c#123']}}
        self.assertEqual(expect, row)

#    def test_result(self):                          
#        """test DAS mongocache result method"""
#        query  = "find site where site=T3_CU"
#        data   = {'system':'sitedb', 'site':'T3_CU', 'se': 'www.cornell.edu'}
#        expect = [dict(data)]
#        expire = 60
#        res = self.dasmongocache.update_cache(query, data, expire)
#        for i in res: # update_cache is generator
#            pass
#        result = [i for i in self.dasmongocache.get_from_cache(query)]
#        result.sort()
#        self.assertEqual(expect, result)
#        self.dasmongocache.delete_cache()






#    def test_pagination(self):                          
#        """test DAS mongocache result method with pagination"""
#        query  = "find site where site=T2_UK"
#        expire = 60
#        expect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#        expect = self.dasmongocache.update_cache(query, expect, expire)
#        expect = [i for i in expect]
#        idx    = 1
#        limit  = 3
#        result = [i for i in self.dasmongocache.get_from_cache(query, idx, limit)]
#        result.sort()
#        self.assertEqual(expect[idx:limit+1], result)
#        self.dasmongocache.delete_cache()

#    def test_sorting(self):                          
#        """test DAS mongocache result method with sorting"""
#        query  = "find site where site=T2_UK"
#        expire = 60
#        data = [
#            {'id':0, 'data':'a', 'run':1},
#            {'id':1, 'data':'b', 'run':3},
#            {'id':2, 'data':'c', 'run':2},
#        ]
#        gen = self.dasmongocache.update_cache(query, data, expire)
#        res = [i for i in gen]
#        skey = 'run'
#        order = 'desc'
#        result = [i for i in \
#            self.dasmongocache.get_from_cache(query, skey=skey, order=order)]
#        expect = [
#            {'id':1, 'data':'b', 'run':3},
#            {'id':2, 'data':'c', 'run':2},
#            {'id':0, 'data':'a', 'run':1},
#        ]
#        self.assertEqual(expect, result)
#        skey = 'run'
#        order = 'asc'
#        result = [i for i in \
#            self.dasmongocache.get_from_cache(query, skey=skey, order=order)]
#        expect = [
#            {'id':0, 'data':'a', 'run':1},
#            {'id':2, 'data':'c', 'run':2},
#            {'id':1, 'data':'b', 'run':3},
#        ]
#        self.assertEqual(expect, result)
#        self.dasmongocache.delete_cache()

#    def test_incache(self):                          
#        """test DAS mongocache incache method"""
#        query  = "find site where site=T2_UK"
#        expire = 1
#        expect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#        expect = self.dasmongocache.update_cache(query, expect, expire)
#        expect = [i for i in expect]
#        result = self.dasmongocache.incache(query)
#        self.assertEqual(1, result)
#        time.sleep(2)
#        result = self.dasmongocache.incache(query)
#        self.assertEqual(0, result)
#        self.dasmongocache.delete_cache()
#
# main
#
if __name__ == '__main__':
    unittest.main()

