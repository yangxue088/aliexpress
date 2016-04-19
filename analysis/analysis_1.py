# -*- coding: utf-8 -*-
import collections
import csv
import sys

import types
from pymongo import MongoClient

if __name__ == '__main__':
    prefix = sys.argv[1]

    db = MongoClient().aliexpress

    store_coll = db['{}store'.format(prefix)]

    product_coll = db['{}product'.format(prefix)]

    order_coll = db['{}order'.format(prefix)]

    feedback_coll = db['{}feedback'.format(prefix)]

    products = collections.defaultdict()


    class Product(object):
        def __init__(self, id):
            self.prefix = ''
            self.id = id
            self.url = ''
            self.store = ''
            self.orders = []
            self.feedbacks = []

        def __str__(self):
            return 'prefix: {}, id: {}, url: {}, store: {}, orders: {}, feedback: {}'.format(self.prefix, self.id, self.url, self.store,
                                                                                             len(self.orders), len(self.feedbacks))


    def get_product(id):
        if id not in products:
            products[id] = Product(id)
        return products[id]


    for product in product_coll.find():
        get_product(product['_id']).id = product['_id']
        get_product(product['_id']).prefix = product['prefix']
        get_product(product['_id']).url = product['url']
        get_product(product['_id']).store = product['store']

    for order in order_coll.find():
        get_product(order['_id']).orders = order['orders']

    for feedback in feedback_coll.find():
        get_product(feedback['_id']).feedbacks = feedback['feedbacks']

    with open('../target/products.csv', 'w') as f:
        headers = ['prefix', 'id', 'url', 'store', 'orders', 'feedbacks']

        rows = [dict((key, value) for key, value in product.__dict__.iteritems() if not callable(value) and not key.startswith('__')) for
                product in products.values()]
        for row in rows:
            for key, value in row.iteritems():
                if isinstance(value, collections.Iterable) and not isinstance(value, types.StringTypes):
                    row[key] = len(value)

        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows)

    print 'finish'
