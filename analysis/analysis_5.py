# -*- coding: utf-8 -*-
import csv
import sys

from pymongo import MongoClient

if __name__ == '__main__':
    prefix = sys.argv[1]

    db = MongoClient().aliexpress

    store_coll = db['{}store'.format(prefix)]

    with open('../target/{}store.csv'.format(prefix), 'w') as f:

        headers = ['prefix', 'id', 'url', 'name', 'product', 'positive_feedback', 'positive_score', 'since_time', 'one_month_feedback',
                   'three_month_feedback', 'six_month_feedback', 'twelve_month_feedback', 'overall_feedback']

        rows = []
        for store in store_coll.find():
            rows.append(
                {'prefix': store['prefix'], 'id': store['_id'], 'url': store['url'], 'name': store['name'], 'product': store['product'],
                 'positive_feedback': store['positive_feedback'], 'positive_score': store['positive_score'],
                 'since_time': store['since_time'].strftime('%Y-%m-%d'), 'one_month_feedback': store['one_month_feedback'][0],
                 'three_month_feedback': store['three_month_feedback'][0], 'six_month_feedback': store['six_month_feedback'][0],
                 'twelve_month_feedback': store['twelve_month_feedback'][0], 'overall_feedback': store['overall_feedback'][0]})

        for row in rows:
            for key, value in row.iteritems():
                row[key] = value

        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows)

    print 'finish'
