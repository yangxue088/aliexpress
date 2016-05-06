# -*- coding: utf-8 -*-
import csv
import sys

from pymongo import MongoClient

if __name__ == '__main__':
    prefix = sys.argv[1]

    db = MongoClient().aliexpress

    store_coll = db['{}storefeedback'.format(prefix)]

    with open('../target/{}storefeedback.csv'.format(prefix), 'w') as f:

        headers = ['prefix', 'id', 'product', 'star', 'time']

        rows = []
        for store in store_coll.find():
            for feedback in store['feedbacks']:
                rows.append(
                    {'prefix': store['prefix'], 'id': store['_id'], 'product': feedback['product'], 'star': feedback['star'],
                     'time': feedback['time']})

        for row in rows:
            for key, value in row.iteritems():
                row[key] = value

        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows)

    print 'finish'
