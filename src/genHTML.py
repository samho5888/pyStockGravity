#!/usr/bin/python
# -*- coding: cp950 -*-
#
import sys
import string

import datetime
import calendar

class genSGHtml:
    ''' Generate Stock-Gravity HTML by using Google or Highstock libraries. '''

    stockId = None
    HtmlName = None

    # String of all transaction data in [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity] format.
    stockAll = []

    def __init__(self, stockId = '2002.TW', stockName = '',
                 stockIndProp = '',
                 wm = 30, wq = 72,
                 m20 = False, m60 = False,
                 rg = 10):
        ''' Constructor

            wm: Work-days of a Month, default is for 6 work-days per week).
            wq: Work-days of a Quarter, default is for 6 work-days per week).
            f(x) = (sum(wm days)/wm + sum(wq days)/wq ) / 2
            m20: Draw mean of 20-work-days.
            m60: Draw mean of 60-work-days.
            rg: Rate of gravity range in percent, 0-50 %'''
        self.stockId = stockId
        self.stockName = stockName
        self.stockIndProp = stockIndProp
        self.HtmlName = str(stockId) + '.html'
        self.wm = wm
        self.wq = wq
        self.m20 = m20
        self.m60 = m60
        self.rg = rg

    def __genAvgData(self, stockData = None):
        ''' Generate average data.

            stockData is stockData[int('YYYYMMDD')] = [Open, High, Low, Close, Volume]
            will become
            stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
        '''
        assert stockData != None

        if len(self.stockAll) > 0:
            # Would re-generate it.
            self.stockAll = []

        dateKey = stockData.keys()
        dateKey.sort(reverse=True)

        wd = 5
        for i in range(0, len(dateKey) - wd):
            self.stockAll.append([dateKey[i],
                                  stockData[dateKey[i]]
                                 ])
            v = 0
            for j in range(0, wd):
                v = v + stockData[dateKey[i+j]][3]
            v = float(v / wd)
            self.stockAll[i].append(v)
        wd = 20
        for i in range(0, len(dateKey) - wd):
            v = 0
            for j in range(0, wd):
                v = v + stockData[dateKey[i+j]][3]
            v = float(v / wd)
            self.stockAll[i].append(v)
        wd = 60
        for i in range(0, len(dateKey) - wd):
            v = 0
            for j in range(0, wd):
                v = v + stockData[dateKey[i+j]][3]
            v = float(v / wd)
            self.stockAll[i].append(v)

        stockAvgM = []
        for i in range(0, len(dateKey) - self.wm):
            v = 0
            for j in range(0, self.wm):
                v = v + stockData[dateKey[i+j]][3]
            v = float(v / self.wm)
            stockAvgM.append(v)
        stockAvgQ = []
        for i in range(0, len(dateKey) - self.wq):
            v = 0
            for j in range(0, self.wq):
                v = v + stockData[dateKey[i+j]][3]
            v = float(v / self.wq)
            stockAvgQ.append(v)
        for i in range(0, len(stockAvgQ)):
            v = (stockAvgM[i] + stockAvgQ[i]) / 2
            self.stockAll[i].append(v)

        # Whether be beyond boundary, and add "[H|L]__" for identification.
        if self.__getClose(0) < (self.__getG(0) * (1.0 - self.rg/100.)):
            print u"Caution!! Range=%d~%d Now=%d" % (
                ((self.__getG(0) * (1.0 - self.rg/100.)),
                 (self.__getG(0) * (1.0 + self.rg/100.)), self.__getClose(0)))
            self.HtmlName = "L__" + self.HtmlName
        elif self.__getClose(0) > (self.__getG(0) * (1.0 + self.rg/100.)):
            print u"Caution!! Range=%d~%d Now=%d" % (
                ((self.__getG(0) * (1.0 - self.rg/100.)),
                 (self.__getG(0) * (1.0 + self.rg/100.)), self.__getClose(0)))
            self.HtmlName = "H__" + self.HtmlName

        # Whether the price is growing over the average.
        count = 0
        if self.__getClose(0) > self.__getG(0):
            count += 1
        else:
            count -= 1
        for idx in range(1, 10):
            if (self.__getClose(idx) >= self.__getG(idx) and
                self.__getClose(idx-1) > self.__getClose(idx)):
                count += 1
            else:
                count -= 1
        if count > 0:
            print u"Caution!! Price is growing."
            self.HtmlName = "+" + self.HtmlName


    def __getClose(self, idx):
        # stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
        return self.stockAll[idx][1][3]

    def __getG(self, idx):
        # stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
        return self.stockAll[idx][5]

    def __getAvg05(self, idx):
        # stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
        return self.stockAll[idx][2]

    def __getAvg20(self, idx):
        # stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
        return self.stockAll[idx][3]

    def __getAvg60(self, idx):
        # stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
        return self.stockAll[idx][4]

    def __genHtml_Google(self):
        ''' Generate HTML by using Google Chart Tools: Visualization Annotated Time Line '''
        assert len(self.stockAll) > 0

        f = open(self.HtmlName, 'wb')
        s = \
'''
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>%s %s %s</title>
        <script type='text/javascript' src='https://www.google.com/jsapi'></script>
        <!--[if lt IE 9]>
        <script src="https://raw.github.com/aFarkas/html5shiv/master/src/html5shiv.js"></script>
        <![endif]-->
        <script type='text/javascript'>
            google.load('visualization', '1', {'packages':['annotatedtimeline']});
            google.setOnLoadCallback(drawChart);
            function drawChart() {
                var data = new google.visualization.DataTable();
                data.addColumn('date', 'Date');
                data.addColumn('number', 'Close');
                data.addColumn('number', 'Avg_G');
                data.addColumn('number', 'Avg_loG');
                data.addColumn('number', 'Avg_hiG');
''' % (self.stockId, self.stockName, self.stockIndProp)
        if self.m20:
                s += '''
                data.addColumn('number', 'Avg_20');'''
        if self.m60:
                s += '''
                data.addColumn('number', 'Avg_60');'''
        s += '''
                data.addRows([\n'''
        f.write(s.encode("UTF-8"))

        for i in range(0, len(self.stockAll) - self.wq):
            # stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
            sd = str(self.stockAll[i][0])
            sl = len(sd)
            d = []
            d.append(sd[0:sl-4])
            d.append(sd[sl-4:sl-2])
            d.append(sd[sl-2:sl])
            # Note: Month from 0
            s = '                    [ new Date(' + str(int(d[0]) + 1911) + ', ' + str(int(d[1]) - 1) + ', ' + str(d[2]) + '), '
            s += str(self.__getClose(i)) + ', '
            s += (str(self.__getG(i)) + ', ' +
                 str(self.__getG(i) * (1.0 - self.rg/100.)) + ', ' +
                 str(self.__getG(i) * (1.0 + self.rg/100.)))
            if self.m20 or self.m60:
                s += ', '
                if self.m20:
                    s += str(self.__getAvg20(i))
                    if self.m60:
                        s += ', '
                if self.m60:
                    s += str(self.__getAvg60(i))
            s += ' ]'
            if i == (len(self.stockAll) - self.wq - 1):
                s += '\n'
            else:
                s += ',\n'
            f.write(s.encode("UTF-8"))

        s = \
'''
                ]);

                var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('chart_div'));
                chart.draw(data, { 'displayAnnotations': 'true',
                                   'scaleType': 'maximized',
                                   'displayExactValues': 'true',
                                   'colors': ['#0000FF', '#222222', '#00FF00', '#FF0000', '#60FF60', '#FF6060']});
             }
        </script>
    </head>
    <body>
        Stock-ID: %s</br>
        Stock-Name: %s</br>
        Stock-Property: %s
        <div id='chart_div' style='width: 800px; height: 400px;'></div>
    </body>
</html>
''' % (str(self.stockId), self.stockName, self.stockIndProp)
        f.write(s.encode("UTF-8"))

        f.close()
        print u'Showed on '+ self.HtmlName +'.\n'

    def __genHtml_Highstock(self):
        ''' Generate HTML by using HighStock library. '''
        assert (len(self.stockAll) - self.wq) > 0

        f = open(self.HtmlName, 'wb')
        s = \
'''
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>%s %s %s</title>
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <script type="text/javascript">
            $(function() {
            var data = ([
''' % (self.stockId, self.stockName, self.stockIndProp)
        f.write(s.encode("UTF-8"))

        for i in range(len(self.stockAll) - self.wq - 1,  -1,  -1):
            sd = str(self.stockAll[i][0])
            sl = len(sd)
            d = []
            d.append(sd[0:sl-4])
            d.append(sd[sl-4:sl-2])
            d.append(sd[sl-2:sl])
            # Date
            Sd = datetime.datetime(int(d[0]) + 1911, int(d[1]), int(d[2]))
            St = calendar.timegm(Sd.utctimetuple()) * 1000
            # stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity]
            # Date, [open, high, low, close, volume], Avg, Avg_l, Avg_h
            s = '[ ' + str(St)
            for j in range(0, 5):
               s += ',' + str(self.stockAll[i][1][j])
            s += (',' + str(self.__getG(i)) + ', ' +
                 str(self.__getG(i) * (1.0 - self.rg/100.)) + ', ' +
                 str(self.__getG(i) * (1.0 + self.rg/100.)))
            if self.m20 or self.m60:
                s += ', '
                if self.m20:
                    s += str(self.__getAvg20(i))
                    if self.m60:
                        s += ', '
                if self.m60:
                    s += str(self.__getAvg60(i))
            s += ' ]'
            if i == 0:
                s += '\n'
            else:
                s += ',\n'
            f.write(s.encode("UTF-8"))

        s = '''
                ]);
        // split the data set into ohlc and volume
        var ohlc = [],
            volume = [],
            avg = [],
            avgL = [],
            avgH = [];'''
        if self.m20:
            s += '''
        var avg20 = [];'''
        if self.m60:
            s += '''
        var avg60 = [];'''

        s += '''
        var dataLength = data.length;

        for (i = 0; i < dataLength; i++) {
            ohlc.push([
                data[i][0], // the date
                data[i][1], // open
                data[i][2], // high
                data[i][3], // low
                data[i][4] // close
            ]);

            volume.push([
                data[i][0], // the date
                data[i][5] // the volume
            ]);

            avg.push([
                data[i][0],
                data[i][6] // the GAvg
            ]);

            avgL.push([
                data[i][0],
                data[i][7] // the GAvg low
            ]);

            avgH.push([
                data[i][0],
                data[i][8] // the GAvg high
            ]);'''
        if self.m20:
            s += '''

            avg20.push([
                data[i][0],
                data[i][9] // the GAvg high
            ]);'''
        if self.m60:
            s += '''

            avg60.push([
                data[i][0],
                data[i][10] // the GAvg high
            ]);'''
        s += '''

        }

        // set the allowed units for data grouping
        var groupingUnits = [[
            'day',                         // unit name
            [1]                             // allowed multiples
        ], [
            'week',                         // unit name
            [1]                             // allowed multiples
        ], [
            'month',
            [1, 2, 3, 4, 6]
        ]];

        // create the chart
        chart = new Highcharts.StockChart({
            chart: {
                renderTo: 'container',
                alignTicks: false
            },

            rangeSelector: {
                selected: 6
            },

            title: {
                text: 'AAPL Historical'
            },

            yAxis: [{
                title: {
                    text: 'OHLC'
                },
                height: 200,
                lineWidth: 2
            }, {
                title: {
                    text: 'Volume'
                },
                top: 300,
                height: 100,
                offset: 0,
                lineWidth: 2
            }],

            series: [{
                type: 'candlestick',
                name: 'Price',
                data: ohlc,
                dataGrouping: {
                    units: groupingUnits
                }
            }, {
                name : 'GAVG',
                data : avg,
                color: '#222222',
                tooltip: {
                    valueDecimals: 2
                }
            }, {
                name : 'GAVG_L',
                data : avgL,
                color: '#00FF00',
                tooltip: {
                    valueDecimals: 2
                }
            }, {
                name : 'GAVG_H',
                data : avgH,
                color: '#FF0000',
                tooltip: {
                    valueDecimals: 2
                }
            }, {
                type: 'column',
                name: 'Volume',
                data: volume,
                yAxis: 1,
                dataGrouping: {
                    units: groupingUnits
                }
            }'''

        if self.m20:
            s += '''
             , {
                name: 'Avg20',
                data: avg20,
                color: '#60FF60',
                tooltip: {
                    valueDecimals: 2
                }
            }'''
        if self.m60:
            s += '''
             , {
                name: 'Avg60',
                data: avg60,
                color: '#FF6060',
                tooltip: {
                    valueDecimals: 2
                }
            }'''
        s += '''
            ]
        });
});
        </script>
    </head>
    <body>
        <script src="http://code.highcharts.com/stock/highstock.js"></script>
        <script src="http://code.highcharts.com/stock/modules/exporting.js"></script>
        Stock-ID: %s</br>
        Stock-Name: %s</br>
        Stock-Property: %s
        <div id="container" style="width: 800px; height: 500px;"></div>
    </body>
</html>
''' % (str(self.stockId), self.stockName, self.stockIndProp)
        f.write(s.encode("UTF-8"))

        f.close()
        print u'Showed on '+ self.HtmlName +'.\n'

    def genHtml(self, stockData = None, form = 'Google'):
        ''' Generate HTML by using Google Chart Tools or HighStock.

            form: 'Google' or 'Highstock'
            stockAll is [YYYYMMDD, [Open, High, Low, Close, Volume], Avg05, Avg20, Avg60, Gravity] '''
        if stockData is None:
            self.HtmlName = None
            print u"Invalid data."
            return

        self.__genAvgData(stockData)
        if form == 'Google':
            self.__genHtml_Google()
        elif form == 'Highstock':
            self.__genHtml_Highstock()
        else:
            print u"Unknown form, please use 'Google' or 'Highstock'"

if __name__ == '__main__':
    pass

