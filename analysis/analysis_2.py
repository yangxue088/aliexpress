# -*- coding: utf-8 -*-
import sys

from pymongo import MongoClient

if __name__ == '__main__':
    prefix = sys.argv[1]

    db = MongoClient().aliexpress

    order_coll = db['{}order'.format(prefix)]

    for result in order_coll.find({'_id': '32621542531'}):

        print 'len: {}'.format(len(result['orders']))

        for date in sorted([order['date'] for order in result['orders']], reverse=True):
            print date
