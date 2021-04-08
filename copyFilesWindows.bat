@echo off
for /f "delims=" %%# in ('powershell get-date -format "{yyyyMMdd}"') do @set _date=%%#
echo %_date%

robocopy C:\source\%_date% C:\destination\%_date%\ /e ]  /NFL /NJH