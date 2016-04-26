# -*- coding: utf-8 -*-
import collections
import csv
import datetime
import sys

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
            self.percent_num = 0
            self.rantings_num = 0
            self.order_num = 0
            self.orders = []
            self.feedbacks = []

        def __str__(self):
            return 'prefix: {}, id: {}, url: {}, store: {}, percent: {}, rating: {}, order: {}, orders: {}, feedback: {}'.format(
                self.prefix, self.id, self.url, self.store,
                self.percent_num, self.rantings_num, self.order_num, len(self.orders), len(self.feedbacks))


    def get_product(id):
        if id not in products:
            products[id] = Product(id)
        return products[id]


    for product in product_coll.find():
        get_product(product['_id']).id = product['_id']
        get_product(product['_id']).prefix = product['prefix']
        get_product(product['_id']).url = product['url']
        get_product(product['_id']).store = product['store']
        get_product(product['_id']).percent_num = product['percent_num']
        get_product(product['_id']).rantings_num = product['rantings_num']
        get_product(product['_id']).order_num = product['order_num']

    for order in order_coll.find():
        get_product(order['_id']).orders = order['orders']

    for feedback in feedback_coll.find():
        get_product(feedback['_id']).feedbacks = feedback['feedbacks']

    with open('../target/{}.csv'.format(prefix), 'w') as f:
        headers = ['prefix', 'id', 'url', 'store', 'orders', 'feedbacks', 'first_order', 'first_feedback', '4_month_orders',
                   '3_month_orders', '2_month_orders', '1_month_orders', '4_month_feedbacks',
                   '3_month_feedbacks', '2_month_feedbacks', '1_month_feedbacks']

        rows = []
        for product in products.values():
            print 'product: {}'.format(product)

            if product.orders:
                first_order = min(product.orders, key=lambda o: o['date'])['date'].strftime('%Y-%m-%d')
            else:
                first_order = 'N/A'

            if product.feedbacks:
                first_feedback = min(product.feedbacks, key=lambda o: o['time'])['time'].strftime('%Y-%m-%d')
            else:
                first_feedback = 'N/A'

            rows.append(
                {'prefix': product.prefix, 'id': product.id, 'url': product.url, 'store': product.store, 'orders': product.order_num,
                 'feedbacks': product.rantings_num,
                 'first_order': first_order,
                 'first_feedback': first_feedback,
                 '4_month_orders': sum(1 for order in product.orders if order['date'] >= datetime.datetime(2016, 4, 1)),
                 '3_month_orders': sum(1 for order in product.orders if
                                       datetime.datetime(2016, 3, 1) <= order['date'] < datetime.datetime(2016, 4, 1)),
                 '2_month_orders': sum(1 for order in product.orders if
                                       datetime.datetime(2016, 2, 1) <= order['date'] < datetime.datetime(2016, 3, 1)),
                 '1_month_orders': sum(1 for order in product.orders if
                                       datetime.datetime(2016, 1, 1) <= order['date'] < datetime.datetime(2016, 2, 1)),
                 '4_month_feedbacks': sum(1 for feedback in product.feedbacks if feedback['time'] >= datetime.datetime(2016, 4, 1)),
                 '3_month_feedbacks': sum(1 for feedback in product.feedbacks if
                                          datetime.datetime(2016, 3, 1) <= feedback['time'] < datetime.datetime(2016, 4, 1)),
                 '2_month_feedbacks': sum(1 for feedback in product.feedbacks if
                                          datetime.datetime(2016, 2, 1) <= feedback['time'] < datetime.datetime(2016, 3, 1)),
                 '1_month_feedbacks': sum(1 for feedback in product.feedbacks if
                                          datetime.datetime(2016, 1, 1) <= feedback['time'] < datetime.datetime(2016, 2, 1))})

        for row in rows:
            for key, value in row.iteritems():
                row[key] = value

        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows)

    print 'finish'
