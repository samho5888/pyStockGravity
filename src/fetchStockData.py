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
import string

from datetime import date
import urllib
import urllib2
from StringIO import StringIO
import csv

# Local library
import StockIdDb
from TData import *

class fetchStockData:
    ''' Fetching historical data from Yahoo, TWSE, TWO '''
    # Stock price data in
    # stockData[int('YYYYMMDD')] = [Open, High, Low, Close, Volume]
    # stockData is instance reference of TData

    # e.g. 1301.TW
    stockId = ''
    # e.g. 1301
    stockNum = 0
    # e.g. TW
    stockCat = ''
    stockName = ''
    stockIndProp = ''
    years = 2

    def __init__(self, stockId = '2002.TW', years = 2, stockData = None):
        if isinstance(stockData, TData) is not True:
            print u"Incorrect stock data"
            raise ValueError
        try:
            # Using unicode.
            self.stockId = stockId.decode('cp950').encode('utf8')
        except:
            self.stockId = stockId
        if self.stockId[0] != '^':
            self.stockName, self.stockNum, self.stockCat, self.stockIndProp = StockIdDb.queryStockId(stockId)
        self.stockData = stockData
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
            self.__fetchTW()
            if self.stockData.getTCount() == 0:
                # Try TWO
                self.__fetchTWO()
                if self.stockData.getTCount() > 0:
                    self.stockId = str(self.stockNum) + '.TWO'
        elif SId == 'TWO':
            self.__fetchTWO()
            if self.stockData.getTCount() == 0:
                # Try TW
                self.__fetchTW()
                if self.stockData.getTCount() > 0:
                    self.stockId = str(self.stockNum) + '.TW'
        else:
            self.__fetchYahoo()

        if self.stockData.getTCount() <= 0:
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

        if self.stockId[0] == '^':
            sid = self.stockId
        else:
            sid = str(self.stockNum) + '.' + self.stockCat
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
            if False:
                # Use ROC year
                d = str(int(d[0]) - 1911) + d[1] + d[2]
            else:
                d = str(int(d[0])) + d[1] + d[2]
            try:
                V = int(urlData[idx + 5])
                Po = float(urlData[idx + 1])
                Ph = float(urlData[idx + 2])
                Pl = float(urlData[idx + 3])
                Pc = float(urlData[idx + 4])
            except:
                continue
            self.stockData.add(int(d), Po, Ph, Pl, Pc, V)

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
            # 日期,成交股數,成交金額,開盤價,最高價,最低價,收盤價,漲跌價差,成交筆數
            # 101/04/02,"5,100,968","437,884,353",86.90,86.90,85.20,85.20,-1.70,"2,129"
            # Not using uni-code here.
            #
            #   99年09月 2002 中鋼 日收盤價及月平均收盤價(元)
            #   日期,收盤價
            #    99/09/01,"30.30"
            #    99/09/02,"30.40"
            #   月平均收盤價,31.84
            #   說明：以上成交資料採市場交易時間之資料計算。
            uthe_page = unicode(the_page, 'cp950')
            urlData = string.split(uthe_page, u'成交筆數\n')
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
                    continue
                if False:
                    # Use ROC year
                    self.stockData.add(int(d), Po, Ph, Pl, Pc, V)
                else:
                    strd = str(int(d[:3]) + 1911) + d[-4:]
                    self.stockData.add(int(strd), Po, Ph, Pl, Pc, V)
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
            #   上櫃個股日成交資訊查詢\n
            #   股票代碼,4123\n
            #   股票名稱,晟德\n
            #   資料月份,2011年12月\n
            #   日期,成交仟股,成交仟元,開盤,最高,最低,收盤,漲跌,筆數\n
            #   "1000901","52","2,084","39.70","40.10","39.50","39.80","0.40","48"\n
            #   "1000902","26","1,012","39.50","39.80","39.50","39.70","-0.10","18"\n
            # Not using uni-code here.
            uthe_page = unicode(the_page, 'cp950')
            urlData = string.split(uthe_page, u'筆數\n')
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
                    V = int(V) * 1000
                    Po = float(Po)
                    Ph = float(Ph)
                    Pl = float(Pl)
                    Pc = float(Pc)
                except:
                    continue
                if False:
                    # Use ROC year
                    self.stockData.add(int(d), Po, Ph, Pl, Pc, V)
                else:
                    strd = str(int(d[:3]) + 1911) + d[-4:]
                    self.stockData.add(int(strd), Po, Ph, Pl, Pc, V)
            b.close()

#
# Test case
#

def main(argv=None):
    stockId = '2002.TW'
    td = TData(stockId)
    fd = fetchStockData(stockId = stockId, years = 1, stockData = td)
#    fd.fetchData(svrId = 'Yahoo')
    fd.fetchData()
    print td.getMean(mean = 5, PorV = 0)

if __name__ == '__main__':
    sys.exit(main())
