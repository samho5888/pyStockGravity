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

import os
import platform
import shutil

import wx
import webbrowser

from fetchStockData import fetchStockData
from genHTML import genSGHtml
from TData import *


class wxStockGravity(wx.Frame):

    def __init__(self, parent, title):
        super(wxStockGravity, self).__init__(parent, title=title, size=(450, 300))

        self.InitUI()
        self.Centre( wx.BOTH )
        self.Show(True)

    def InitUI(self):
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        bSizer_Option = wx.BoxSizer( wx.HORIZONTAL )

        SG_ServerChoices = [ u"by end-notation", u"Yahoo" ]
        self.SG_Server = wx.RadioBox( self, wx.ID_ANY, u"Default Server", wx.DefaultPosition, wx.DefaultSize, SG_ServerChoices, 1, wx.RA_SPECIFY_COLS )
        self.SG_Server.SetSelection( 0 )
        bSizer_Option.Add( self.SG_Server, 0, wx.ALL, 5 )

        SG_ChartChoices = [ u"Google Chart: Annotated Time Line", u"Highcharts: Highstock" ]
        self.SG_Chart = wx.RadioBox( self, wx.ID_ANY, u"Chart Type", wx.DefaultPosition, wx.DefaultSize, SG_ChartChoices, 1, wx.RA_SPECIFY_COLS )
        self.SG_Chart.SetSelection( 0 )
        bSizer_Option.Add( self.SG_Chart, 0, wx.ALL, 5 )


        bSizer3.Add( bSizer_Option, 1, 0, 5 )

        gbSizer1 = wx.GridBagSizer( 0, 0 )
        gbSizer1.SetFlexibleDirection( wx.BOTH )
        gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.StockID = wx.TextCtrl( self, wx.ID_ANY, u"1301.TW", wx.Point( -1,-1 ), wx.Size( -1,30 ), wx.TE_LEFT )
        self.StockID.SetMaxLength( 12 )
        self.StockID.Bind(wx.EVT_KEY_DOWN, self.StockIDOnKeyDown)
        gbSizer1.Add( self.StockID, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.btnShowIt = wx.Button( self, wx.ID_ANY, u"Show it", wx.Point( -1,-1 ), wx.Size( -1,30 ), 0 )
        self.btnShowIt.Bind(wx.EVT_BUTTON, self.OnbtnShowIt)
        gbSizer1.Add( self.btnShowIt, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        choice_YearChoices = [ u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8" ]
        self.choice_Year = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), choice_YearChoices, 0 )
        self.choice_Year.SetSelection( 1 )
        gbSizer1.Add( self.choice_Year, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.SText_Years = wx.StaticText( self, wx.ID_ANY, u"Years", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.SText_Years.Wrap( -1 )
        gbSizer1.Add( self.SText_Years, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.SText_WM = wx.StaticText( self, wx.ID_ANY, u"Work-days per Month", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
        self.SText_WM.Wrap( -1 )
        gbSizer1.Add( self.SText_WM, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.SpinCtrl_WM = wx.SpinCtrl( self, wx.ID_ANY, u"20", wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 1, 31, 20 )
        gbSizer1.Add( self.SpinCtrl_WM, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.SText_WQ = wx.StaticText( self, wx.ID_ANY, u"Work-days per Quarter", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.SText_WQ.Wrap( -1 )
        gbSizer1.Add( self.SText_WQ, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.SpinCtrl_WQ = wx.SpinCtrl( self, wx.ID_ANY, u"65", wx.DefaultPosition, wx.Size( 50,-1 ), wx.SP_ARROW_KEYS, 32, 91, 65 )
        gbSizer1.Add( self.SpinCtrl_WQ, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        bSizer3.Add( gbSizer1, 1, wx.EXPAND, 5 )

        self.SetSizer( bSizer3 )
        self.Layout()

        self.SetTitle('Stock Gravity')
        self.html_dst = 'html'

    def OnbtnShowIt(self, e):
        sID = self.StockID.GetValue()
        #wx.MessageBox(str(sID), 'Info', wx.OK | wx.ICON_INFORMATION)
        if len(sID) == 0:
            wx.MessageBox('Invalid stock ID, e.g. 1301.TW', 'Error', wx.OK | wx.ICON_INFORMATION)
            return

        self.btnShowIt.SetLabel('In Progress')
        self.btnShowIt.Disable()
        try:
            td = TData(sID)
            # Fetcing data
            stkData = fetchStockData(stockId = sID,
                                     years=(self.choice_Year.GetCurrentSelection() +1),
                                     stockData = td)
            if self.SG_Server.GetSelection() == 0:
                # By end-notation
                stkData.fetchData()
            else:
                # Yahoo
                stkData.fetchData('Yahoo')

            if td.getTCount() < 120:
                wx.MessageBox('Too few data for decision-making: ' + str(len(stkData.stockData)),
                              'Error', wx.OK | wx.ICON_INFORMATION)
                self.btnShowIt.SetLabel('Show it')
                self.btnShowIt.Enable()
                return
            else:
                if stkData.stockId[0] == '^':
                    sID = stkData.stockId
                else:
                    sID = str(stkData.stockNum) + '.' + stkData.stockCat
                # Generate Stock-Gravity HTML
                stkHtml = genSGHtml(stockId = sID,
                                    stockName = stkData.stockName,
                                    stockIndProp = stkData.stockIndProp,
                                    wm = self.SpinCtrl_WM.GetValue(),
                                    wq = self.SpinCtrl_WQ.GetValue())
                if self.SG_Chart.GetSelection() == 0:
                    # Google
                    stkHtml.genHtml(stockData = stkData.stockData, form = 'Google')
                else:
                    # Highstock
                    stkHtml.genHtml(stockData = stkData.stockData, form = 'Highstock')
                hName = stkHtml.HtmlName
        except:
            wx.MessageBox('Invalid stock ID, e.g. 1301.TW', 'Error', wx.OK | wx.ICON_INFORMATION)
            self.btnShowIt.SetLabel('Show it')
            self.btnShowIt.Enable()
            return

        if hName == None:
            wx.MessageBox('Invalid stock ID, e.g. 1301.TW', 'Error', wx.OK | wx.ICON_INFORMATION)
            self.btnShowIt.SetLabel('Show it')
            self.btnShowIt.Enable()
            return

        if os.path.exists(self.html_dst) != True:
            os.makedirs(self.html_dst)
        #print hName
        shutil.copyfile(hName, self.html_dst+'/' + hName)
        os.remove(hName)
        if platform.system() == 'Windows':
            fn = os.getcwd() + '\\' + self.html_dst + '\\' + hName
        else:
            fn = os.getcwd() + '/' + self.html_dst + '/' + hName
        #print fn
        webbrowser.open_new_tab(fn)

        del td
        del stkData
        del stkHtml
        self.btnShowIt.SetLabel('Show it')
        self.btnShowIt.Enable()
        e.Skip()

    def StockIDOnKeyDown(self, e):
        if e.GetKeyCode() == wx.WXK_RETURN:
            self.OnbtnShowIt(e)
        e.Skip()

    def OnCloseWindow(self, e):
        if os.path.exists(self.html_dst) == True:
            shutil.rmtree(self.html_dst)
        self.Destroy()

if __name__ == '__main__':
    appDebug = False
    app = wx.App(redirect=False)
    wxStockGravity(None, title='wxSG')
    app.MainLoop()
