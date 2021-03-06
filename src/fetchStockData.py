#!/usr/bin/python
# -*- coding: cp950 -*-
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
import string

from datetime import date
import urllib
import urllib2
from StringIO import StringIO
import csv

# Local library
import StockIdDb

class fetchStockData:
    ''' Fetching historical data from Yahoo, TWSE, TWO '''
    # Stock price data in
    # stockData[int('YYYYMMDD')] = [Open, High, Low, Close, Volume]
    #stockData = {}

    # e.g. 1301.TW
    stockId = ''
    # e.g. 1301
    stockNum = 0
    # e.g. TW
    stockCat = ''
    stockName = ''
    stockIndProp = ''
    years = 2

    def __init__(self, stockId = '2002.TW', years = 2):
        try:
            # Using unicode.
            self.stockId = stockId.decode('cp950').encode('utf8')
        except:
            self.stockId = stockId
        self.stockData = {}
        if years > 0:
            self.years = years
        else:
            self.years = 2

    def fetchData(self, svrId = None):
        '''
            Fetcing data from svrId

            svrId is 'Yahoo'
        '''
        if svrId == 'Yahoo':
            SId = svrId
        else:
            # Parsing the prefix and postfix
            if self.stockId[0] == '^':
                SId = 'Yahoo'
            else:
                SId = self.stockCat

        if SId == 'TW':
            self.__QueryStock()
            self.__fetchTW()
            if len(self.stockData) == 0:
                # Try TWO
                self.__fetchTWO()
                if len(self.stockData) > 0:
                    self.stockId = str(self.stockNum) + '.TWO'
        elif SId == 'TWO':
            self.__QueryStock()
            self.__fetchTWO()
            if len(self.stockData) == 0:
                # Try TW
                self.__fetchTW()
                if len(self.stockData) > 0:
                    self.stockId = str(self.stockNum) + '.TW'
        else:
            self.__fetchYahoo()

        if len(self.stockData) <= 0:
            print u"Fetching " + str(self.stockId) + ' failed\n'

    def _countDuration(self, D):
        # Counting set of month duration to fetch data. D is []
        t = date.today()
        for m in range(t.month, 13):
            D.append((t.year - self.years, m))
        if self.years > 1:
            for y in range(t.year - self.years + 1, t.year):
                for m in range(1, 13):
                    D.append((y, m))
        for m in range(1, t.month+1):
            D.append((t.year, m))

    def __fetchYahoo(self):
        today = date.today()

        if self.stockCat != '':
            sid = str(self.stockNum) + '.' + self.stockCat
        else:
            sid = self.stockId
        csvFile = 'http://ichart.finance.yahoo.com/table.csv?s=' + str(sid)
        csvFile += '&a=' + str(today.month)
        csvFile += '&b=' + str(today.day)
        csvFile += '&c=' + str(today.year - self.years)
        csvFile += '&d=' + str(today.month)
        csvFile += '&e=' + str(today.day)
        csvFile += '&f=' + str(today.year)

        urlData = urllib.urlopen(csvFile).read()
        if urlData[0] == '<':
            print u"Not Found"
            raise ValueError

        #
        # Format is Date,       Open, High,  Low,Close,Volume,Adj Close
        #           2011-09-28,34.60,34.60,33.35,33.60, 54000,33.60
        #           2011-09-27,34.00,34.45,33.00,33.20, 71000,33.20
        # with '\n' as line-terminator
        urlData = string.replace(urlData, '\n',  ',')
        urlData = string.split(urlData, ',')
        # last '\n' is now ','
        urlData = urlData[:(len(urlData) - 1)]

        for idx in range(7, len(urlData), 7):
            d = urlData[idx]
            d = string.split(d, '-')
            d = str(int(d[0]) - 1911) + d[1] + d[2]
            try:
                V = int(urlData[idx + 5])
                Po = float(urlData[idx + 1])
                Ph = float(urlData[idx + 2])
                Pl = float(urlData[idx + 3])
                Pc = float(urlData[idx + 4])
            except:
                continue;
            self.stockData[int(d)] = [Po, Ph, Pl, Pc, V]

    def __fetchTW(self):
        '''
            Fetch from TWSE

            Example: http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report201204/201204_F3_1_8_2002.php&type=csv
        '''
        D = []
        self._countDuration(D)

        for ym in D:
            y = ym[0]
            m = ym[1]
            csvFile = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report'
            csvFile += str(y)
            if m < 10:
                csvFile += '0' + str(m)
                csvFile += '/' + str(y) + '0' + str(m) + '_F3_1_8_' + str(self.stockNum) + '.php&type=csv'
            else:
                csvFile += str(m)
                csvFile += '/' + str(y) + str(m) + '_F3_1_8_' + str(self.stockNum) + '.php&type=csv'
            the_page = urllib.urlopen(csvFile).read()
            if len(the_page) == 0:
                continue

            # Format is:
            # ら戳,Θユ计,Θユ肂,秨絃基,程蔼基,程基,Μ絃基,害禴基畉,Θユ掸计
            # 101/04/02,"5,100,968","437,884,353",86.90,86.90,85.20,85.20,-1.70,"2,129"
            # Not using uni-code here.
            #
            #   9909る 2002 い葵 らΜ絃基のるキАΜ絃基(じ)
            #   ら戳,Μ絃基
            #    99/09/01,"30.30"
            #    99/09/02,"30.40"
            #   るキАΜ絃基,31.84
            #   弧Θユ戈蹦カ初ユ丁ぇ戈璸衡
            urlData = string.split(the_page, 'Θユ掸计\n')
            urlData = urlData[1]

            b = StringIO(urlData)
            r = csv.reader(b, skipinitialspace=True)
            for row in r:
                # Date
                d = string.replace(row[0], '/', '')
                # Volume
                v = string.replace(row[1], ',', '')
                try:
                    V = int(v)
                    Po = float(row[3])
                    Ph = float(row[4])
                    Pl = float(row[5])
                    Pc = float(row[6])
                except:
                    continue;
                self.stockData[int(d)] = [Po, Ph, Pl, Pc, V]
            b.close()

    def __fetchTWO(self):
        '''
            Fetch from OTC
        '''
        D = []
        self._countDuration(D)

        url = 'http://www.otc.org.tw/ch/stock/aftertrading/daily_trading_info/download_st43.php'
        for ym in D:
            y = ym[0]
            m = ym[1]
            values = { 'stk_no' : self.stockNum, 'yy' : str(y), 'mm' : str(m) }
            postData = urllib.urlencode(values)

            req = urllib2.Request(url, postData)
            response = urllib2.urlopen(req)
            the_page = response.read()
            if len(the_page) == 0:
                continue

            # Format is:
            #   耫らΘユ戈癟琩高\n
            #   布絏,4123\n
            #   布嘿,言紈\n
            #   戈る,201112る\n
            #   ら戳,Θユ,Θユじ,秨絃,程蔼,程,Μ絃,害禴,掸计\n
            #   "1000901","52","2,084","39.70","40.10","39.50","39.80","0.40","48"\n
            #   "1000902","26","1,012","39.50","39.80","39.50","39.70","-0.10","18"\n
            # Not using uni-code here.
            urlData = string.split(the_page, '掸计\n')
            if len(urlData[1]) < 2:
                continue
            urlData = urlData[1]

            b = StringIO(urlData)
            r = csv.reader(b, skipinitialspace=True)
            for row in r:
                d = string.replace(row[0], '"', '')
                V = string.replace(row[1], ',', '')
                V = string.replace(V, '"', '')
                Po = string.replace(row[3], ',', '')
                Po = string.replace(Po, '"', '')
                Ph = string.replace(row[4], ',', '')
                Ph = string.replace(Ph, '"', '')
                Pl = string.replace(row[5], ',', '')
                Pl = string.replace(Pl, '"', '')
                Pc = string.replace(row[6], ',', '')
                Pc = string.replace(Pc, '"', '')
                try:
                    V = int(V) * 1000;
                    Po = float(Po);
                    Ph = float(Ph);
                    Pl = float(Pl);
                    Pc = float(Pc);
                except:
                    continue;
                self.stockData[int(d)] = [Po, Ph, Pl, Pc, V]
            b.close()

    def __QueryStock(self):
        '''
            Query the cataglory of stock
            .TW: http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=2
            .TWO: http://brk.tse.com.tw:8000/isin/C_public.jsp?strMode=4
        '''
        sDB = StockIdDb.StockIdDb()
        sDB.chkDB()
        if self.stockId[0] >= '0' and self.stockId[0] <= '9':
            idx = 0
            for idx in range(len(self.stockId)):
                if self.stockId[idx] >= '0' and self.stockId[idx] <= '9':
                    idx += 1
                else:
                    break
            self.stockNum = self.stockId[0:idx]
            rst = sDB.queryByNum(self.stockNum)
            if rst:
                self.stockName = rst[0]
                self.stockCat = rst[1]
                self.stockIndProp = rst[2]
            else:
                print u"Query failed?"
                raise OSError
        else:
            # Query by Name
            rst = sDB.queryByName(self.stockId)
            if rst:
                self.stockName = self.stockId
                self.stockNum = rst[0]
                self.stockCat = rst[1]
                self.stockIndProp = rst[2]
            else:
                print u"Query failed?"
                raise OSError

if __name__ == '__main__':
    pass
