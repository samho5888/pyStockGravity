#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys

# Local library
from TData import *
# For test case
from fetchStockData import *

class ChkMean:
    '''
        Check the price-trend against to mean of N-days.

    '''

    def __init__(self, stockId = '2002.TW', tdata = None):
        self.stockId = stockId
        # ID of stock, using Yahoo Finance format.
        self.__stockId = ''
        # Transaction data in dictionary format.
        if isinstance(tdata, TData) is not True:
            print u"Incorrect stock data"
            raise ValueError
        self.__tdata = tdata
        self.__dateKey = tdata.keys()
        self.__dateKey.sort(reverse=True)

        self.__mean = {}

    def isGrowing(self, DaysOfMean = 5, DaysOfObs = 1, TermsOfObs = 10):
        '''
            - Is price growing.
              1. Growing everyday.
              2. Growing along N-Mean
            - DaysOfMean: How many days for mean
            - DaysOfObs: How many days as observation duration,
                         e.g. 5 mean observing per 5 wor-day.
            - TermsOfObs: how many terms or section for daysOfObs
        '''
        if (DaysOfMean <= 0) or (DaysOfObs <= 0) or (TermsOfObs <= 0):
            print u"Not enough transaction data."
            raise ValueError
        elif self.__tdata.getTCount() < (DaysOfMean + DaysOfObs * TermsOfObs):
            print u"Not enough transaction data."
            raise ValueError
        md = 'm' + str(DaysOfMean)
        if md not in self.__mean:
            self.__mean[md] = self.__tdata.getMean(mean = DaysOfMean, PorV = 0)

        mean = self.__mean[md]
        cnt_price = 0
        cnt_mean = 0
        # Latest day
        d = self.__dateKey[0]
        pn = self.__tdata.get(d)[3]
#        print d, pn
        p0 = pn
        if pn > mean[d]:
            cnt_mean += 1
        for i in range(DaysOfObs, DaysOfObs * TermsOfObs, DaysOfObs):
            d = self.__dateKey[i]
            p = self.__tdata.get(d)[3]
#            print d, p
            if p:
                # Compare price and mean
                if p > mean[d]:
                    cnt_mean += 1
                elif p < mean[d]:
                    cnt_mean -= 1
                # Compare price and price-next-day
                if p < pn:
                    cnt_price += 1
                elif p > pn:
                    cnt_price -= 1
                pn = p
            else:
                print u"Incorrect price at " + d
        # More day for price comparing
        d = self.__dateKey[DaysOfObs * TermsOfObs]
        p = self.__tdata.get(d)[3]
#        print d, p
        if p < pn:
            cnt_price += 1
        elif p > pn:
            cnt_price -= 1

        print u"DaysOfMean: %d, DaysOfObs: %d, TermsOfObs: %d" % (DaysOfMean, DaysOfObs, TermsOfObs)
        print u"cnt_price: %d, cnt_mean: %d" % (cnt_price, cnt_mean)
        if p0 > pn:
            print u"Price: (+) %f (%f%%)" % ((p0-pn), (p0-pn)*100.0/pn)
        elif p0 < pn:
            print u"Price: (-) %f (%f%%)" % ((pn-p0), (pn-p0)*100.0/pn)
        else:
            print u"Price is not changed."



def main(argv=None):
    stockId = '2002.TW'
    td = TData(stockId)
    fd = fetchStockData(stockId = stockId, years = 1, stockData = td)
    fd.fetchData(svrId = 'Yahoo')
#    fd.fetchData()
#    print td.getMean(mean = 5, PorV = 0)
    cm = ChkMean(stockId, td)
    cm.isGrowing(DaysOfMean = 5, DaysOfObs = 1, TermsOfObs = 10)
    cm.isGrowing(DaysOfMean = 5, DaysOfObs = 5, TermsOfObs = 10)
    cm.isGrowing(DaysOfMean = 20, DaysOfObs = 1, TermsOfObs = 10)
    cm.isGrowing(DaysOfMean = 20, DaysOfObs = 5, TermsOfObs = 10)

if __name__ == '__main__':
    sys.exit(main())

