@echo off

SET StockGravity="C:\Users\samho\Downloads\sg\1106\src\StockGravity\StockGravity"

rem Stock number e.g. "^TWII", "3019.TW" or "8069.TWO"
SET STOCK=stock_list.txt

if not exist html (
    mkdir html
)

for /f %%s in (%STOCK%) do (
    echo Fetching %%s...
rem     %StockGravity% %%s
    %StockGravity% %%s --yahoo
)
move /y *.html html\

pause
