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
import os

import urllib
from pyquery import PyQuery as pq
import sqlite3

class StockIdDb:
    '''
        Collect stock number, name, catagory, industry-property.
        * TW:  http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=2
        * TWO: http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=4
    '''
    def __init__(self):
        self.dbPath = 'db'
        self.dbName = 'StockID.db'
        self.dbLocation = self.dbPath + '/' + self.dbName
        try:
            os.mkdir(self.dbPath)
        except OSError:
            pass
        except:
            print "Can not locate folder of DB."
            raise OSError

    def refreshDB(self):
        conn = None
        try:
            con = sqlite3.connect(self.dbLocation)
            cur = con.cursor()

        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)

        # (Number, Name, Catalog of Stock Market, Industry Property)
        cur.executescript("""
            DROP TABLE IF EXISTS StockId;
            CREATE TABLE StockId(SNum TEXT, SName TEXT, SCat TEXT, SIndProp TEXT);""")
        con.commit()
        self.__collect_TW(cur)
        con.commit()
        self.__collect_TWO(cur)
        con.commit()

        if con:
            con.close()

    def __collect_TW(self, cur):
        if True:
            f = urllib.urlopen('http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=2')
            s = f.read()
            f.close()
            d = pq(unicode(s, 'cp950'))
        else:
            d = pq(url='http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=2')
        p = d('td')
        idx_s = 0
        idx_e = 0
        for idx in range(len(p)):
            if p.eq(idx).html() != None:
                if p.eq(idx).find('b') != []:
                    if p.eq(idx).find('b').text() == u"股票":
                        idx_s = idx + 1
                    elif p.eq(idx).find('b').text() == u"上市認購(售)權證":
                        idx_e = idx - 1
        #print idx_s
        #print idx_e
        for idx in range(idx_s, idx_e, 7):
            t = p.eq(idx).text()
            ts = t.split()
            stockNum = ts[0]
            stockName = ts[1]
            stockCat = 'TW'
            stockIndProp =  p.eq(idx+4).text()
            #print stockNum, stockName, stockCat, stockIndProp
            cmd = ("INSERT INTO StockId VALUES('" + str(stockNum) + "','" +
                   stockName + "','" + stockCat + "','" + stockIndProp + "')")
            cur.executescript(cmd)
        for idx in range(idx_e, len(p)):
            if p.eq(idx).html() != None:
                if p.eq(idx).find('b') != []:
                    if p.eq(idx).find('b').text() == u"ETF":
                        idx_s = idx + 1
                    elif p.eq(idx).find('b').text() == u"臺灣存託憑證":
                        idx_e = idx - 1
        #print idx_s
        #print idx_e
        for idx in range(idx_s, idx_e, 7):
            t = p.eq(idx).text()
            ts = t.split()
            stockNum = ts[0]
            stockName = ts[1]
            stockCat = 'TW'
            stockIndProp =  p.eq(idx+4).text()
            #print stockNum, stockName, stockCat, stockIndProp
            cmd = ("INSERT INTO StockId VALUES('" + str(stockNum) + "','" +
                   stockName + "','" + stockCat + "','" + stockIndProp + "')")
            cur.executescript(cmd)

    def __collect_TWO(self, cur):
        if True:
            f = urllib.urlopen('http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=4')
            s = f.read()
            f.close()
            d = pq(unicode(s, 'cp950'))
        else:
            d = pq(url='http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=4')
        p = d('td')
        idx_s = 0
        idx_e = 0
        for idx in range(len(p)):
            if p.eq(idx).html() != None:
                if p.eq(idx).find('b') != []:
                    if p.eq(idx).find('b').text() == u"ETF":
                        idx_s = idx + 1
                    elif p.eq(idx).find('b').text() == u"股票":
                        idx_e = idx - 1
        #print idx_s
        #print idx_e
        for idx in range(idx_s, idx_e, 7):
            t = p.eq(idx).text()
            ts = t.split()
            stockNum = ts[0]
            stockName = ts[1]
            stockCat = 'TWO'
            stockIndProp =  p.eq(idx+4).text()
            #print stockNum, stockName, stockCat, stockIndProp
            cmd = ("INSERT INTO StockId VALUES('" + str(stockNum) + "','" +
                   stockName + "','" + stockCat + "','" + stockIndProp + "')")
            cur.executescript(cmd)
        for idx in range(idx_e, len(p)):
            if p.eq(idx).html() != None:
                if p.eq(idx).find('b') != []:
                    if p.eq(idx).find('b').text() == u"股票":
                        idx_s = idx + 1
                    elif p.eq(idx).find('b').text() == u"臺灣存託憑證":
                        idx_e = idx - 1
        #print idx_s
        #print idx_e
        for idx in range(idx_s, idx_e, 7):
            t = p.eq(idx).text()
            ts = t.split()
            stockNum = ts[0]
            stockName = ts[1]
            stockCat = 'TWO'
            stockIndProp =  p.eq(idx+4).text()
            #print stockNum, stockName, stockCat, stockIndProp
            cmd = ("INSERT INTO StockId VALUES('" + str(stockNum) + "','" +
                   stockName + "','" + stockCat + "','" + stockIndProp + "')")
            cur.executescript(cmd)

    def chkDB(self, force=False):
        if force == True:
            print "Force to refresh DB."
            self.refreshDB()
        elif os.access(self.dbLocation, os.R_OK):
            return
        else:
            print "DB does not exist, try to refresh it."
            self.refreshDB()

    def queryByNum(self, Num=1301):
        conn = None
        try:
            con = sqlite3.connect(self.dbLocation)
            cur = con.cursor()

        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)

        cmd = "SELECT SName, SCat, SIndProp FROM StockId WHERE SNum='" + Num + "';"
        cur.execute(cmd)
        row = cur.fetchone()
        if con:
            con.close()
        return row

    def queryByName(self, Name=None):
        if Name == None:
            return None
        conn = None
        try:
            con = sqlite3.connect(self.dbLocation)
            cur = con.cursor()

        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)

        # TEXT is unicode.
        cmd = "SELECT SNum, SCat, SIndProp FROM StockId WHERE SName='" + Name + "';"
        cur.execute(cmd)
        row = cur.fetchone()
        if con:
            con.close()
        return row

def queryStockId(stockId = ''):
    '''
        Query the cataglory of stock
        .TW: http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=2
        .TWO: http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=4
    '''
    sDB = StockIdDb()
    sDB.chkDB()
    if stockId[0] >= '0' and stockId[0] <= '9':
        idx = 0
        for idx in range(len(stockId)):
            if stockId[idx] >= '0' and stockId[idx] <= '9':
                idx += 1
            else:
                break
        stockNum = stockId[0:idx]
        rst = sDB.queryByNum(stockNum)
        if rst:
            stockName = rst[0]
            stockCat = rst[1]
            stockIndProp = rst[2]
        else:
            print u"Query failed?"
            raise OSError
    else:
        # Query by Name
        rst = sDB.queryByName(stockId)
        if rst:
            stockName = stockId
            stockNum = rst[0]
            stockCat = rst[1]
            stockIndProp = rst[2]
        else:
            print u"Query failed?"
            raise OSError
    return stockName, stockNum, stockCat, stockIndProp

def main(argv=None):
    db = StockIdDb()
    db.chkDB()
    # Force to refreshDB
    #db.refreshDB()
    print "stockName: %s, stockNum: %s, stockCat: %s, stockIndProp: %s" % queryStockId('1301')
    print "stockName: %s, stockNum: %s, stockCat: %s, stockIndProp: %s" % queryStockId(u'新普')
    return

if __name__ == '__main__':
    sys.exit(main())
