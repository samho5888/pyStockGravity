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

class TData:
    '''
        Store transaction data of stock.
        Transaction data in dictionary format, all is float or int
        {
          YYYYMMDD : [
                       ( Po, Ph, Pl, Pc, V ),                  --> Transaction
                       { 'm5': v5, 'm10': v10, ..., 'G': vg }  --> TODO: Calculation
                     ]
        }

    '''

    def __init__(self, stockId = '2002.TW'):
        self.stockId = stockId
        # ID of stock, using Yahoo Finance format.
        self.__stockId = ''
        # Transaction data in dictionary format.
        self.__tdata = {}

    def add(self, YYYYMMDD, Po, Ph, Pl, Pc, V):
        '''
            Add one item of transaction data.
            YYYYMMDD: date in integer
            Po, Ph, Pl, Pc: Price of open, high, low, close.
            V: Volume (TODO: in 1000 stocks for TW market.)
        '''
        if type(YYYYMMDD) is not type(int()):
            print "Incorrect input"
            return
        else:
            if YYYYMMDD in self.__tdata:
                print "% was added." % YYYYMMDD
            else:
                # TODO: check parameters.
                self.__tdata[YYYYMMDD] = [ (Po, Ph, Pl, Pc, V), {} ]

    def keys(self):
        '''
            Get keys (transaction date), return 0 as not found.
        '''
        return self.__tdata.keys()

    def get(self, YYYYMMDD):
        '''
            Get transaction data, return 0 as not found.
        '''
        if type(YYYYMMDD) is not type(int()):
            print "Incorrect input"
            return 0
        else:
            if YYYYMMDD in self.__tdata:
                return self.__tdata[YYYYMMDD][0]
            else:
                return 0

    def __getitem__(self, index):
        '''
            Overloading of [], like get
        '''
        return self.get(index)

    def getTCount(self):
        '''
            Get transaction counts.
        '''
        return len(self.__tdata)

    def getMean(self, mean = 5, PorV = 0):
        '''
            Get mean data of price,
            mean > 1 and mean < 260 and mean < len(__tdata)
            PorV
                - 0: as Price (Close)
                - 1: as Volume
            return 0 as incorrect mean value
        '''
        if type(mean) is not type(int()):
            print "Incorrect input"
            return 0
        elif (mean <= 1) or (mean > 260) or (mean > len(self.__tdata)):
            print "Incorrect input"
            return 0
        elif (PorV != 0) and (PorV != 1):
            print "Incorrect input"
            return 0

        dateKey = self.__tdata.keys()
        dateKey.sort(reverse=True)
        # Array to store { date: mean }
        ma = {}
        for i in range(0, len(dateKey) - mean + 1):
            v = 0.0
            for j in range(0, mean):
                # Counting sum of close price or volume
                v = v + self.__tdata[dateKey[i+j]][0][3 + PorV]
            v = v / mean
            ma[dateKey[i]] = v
        return ma

def main(argv=None):
    t = TData()
    print "test add -----------"
    t.add(20130501, 1, 2, 3, 4, 5)
    if t.get(12345678) != 0:
        print "Yes"
    else:
        print "No"
    print t.get(20130501)
    print "test mean ----------"
    t.add(20130502, 2, 3, 4, 5, 6)
    t.add(20130503, 3, 4, 5, 6, 7)
    t.add(20130504, 4, 5, 6, 7, 8)
    t.add(20130505, 5, 6, 7, 8, 9)
    t.add(20130506, 6, 7, 8, 9, 10)
    t.add(20130507, 7, 8, 9, 10, 11)
    print "getMean(2, Pirce)"
    print t.getMean(2, 0)
    print "getMean(5, Volume)"
    print t.getMean(5, 1)
    return

if __name__ == '__main__':
    sys.exit(main())