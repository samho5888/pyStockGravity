#!/usr/bin/python
# -*- coding: cp950 -*-
#
import sys
import string
import argparse

from fetchStockData import fetchStockData
from genHTML import genSGHtml

def testCase():
    d = fetchStockData(stockId = '1301.TW', years = 2)
    # 'Yahoo', 'TW', 'TWO'
    d.fetchData('TW')
    h = genSGHtml(d.stockId)
    h.genHtml(d.stockData, 'Google')
#    h.genHtml(d.stockData, 'Highstock')

def main(argv=None):
    parser = argparse.ArgumentParser(description='Stock Gravity.')
    parser.add_argument('SID', type=str, metavar='Stock-ID',
                        help="Stock-ID, e.g. 1301.TW, 6121.TWO, ^TWII")
    parser.add_argument('--years', type=int, default=2,
                        choices=xrange(1,11),
                        help="Years to show, in range 1-10, default: 2")
    parser.add_argument('--form', type=str, default='Google',
                        choices=['Google', 'Highstock'],
                        help="Display in {Google | Highstock} form, default: Google")
    parser.add_argument('--month', type=int, default=22,
                        choices=xrange(1,32),
                        help="Work-days of a month, default: 22")
    parser.add_argument('--quarter', type=int, default=65,
                        choices=range(31,92),
                        help="Work-days of a quarter, default: 65")
    parser.add_argument('--yahoo', action='store_true',
                        help="Fetch data from Yahoo!")
    parser.add_argument('--m20', action='store_true',
                        help="Draw mean of 20-work-days")
    parser.add_argument('--m60', action='store_true',
                        help="Draw mean of 60-work-days")
    parser.add_argument('--rg', type=float, default=10,
                        help="Rate of gravity range in percent. 0-50 (%%)")
    # Test case
    #    args = parser.parse_args('1301.TW --year 5 --form Highstock'.split())
    args = parser.parse_args()
    if args.rg < 0 or args.rg > 50:
        parser.parse_args('-h'.split())
        return

    d = fetchStockData(stockId = args.SID, years=args.years)
    if args.yahoo:
        d.fetchData('Yahoo')
    else:
        d.fetchData()

    if len(d.stockData) < 120:
        print u'Too few data for decision-making: %d' % len(d.stockData)
    else:
        if d.stockId[0] == '^':
            sID = d.stockId
        else:
            sID = str(d.stockNum) + '.' + d.stockCat
        h = genSGHtml(stockId = sID,
                      stockName = d.stockName,
                      stockIndProp = d.stockIndProp,
                      wm = args.month, wq = args.quarter,
                      m20=args.m20, m60=args.m60,
                      rg=args.rg)
        h.genHtml(d.stockData, args.form)

    return

if __name__ == '__main__':
    sys.exit(main())

