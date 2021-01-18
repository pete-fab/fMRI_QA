#!/usr/bin/env python
import datetime as dt
import os, sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import directory

def main():
    today = dt.date.today()
    date_pacs_format = today.strftime("%Y%m%d")
    print(date_pacs_format)
    # dataPaths = directory.getChildrenPaths(dateFolderPath)

if __name__ == "__main__":
    main()