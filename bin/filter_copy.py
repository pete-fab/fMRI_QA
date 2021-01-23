#!/usr/bin/env python

import datetime as dt
import os, sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import directory
import argparse

def main():
    today = dt.date.today()
    date_pacs_format = today.strftime("%Y%m%d")
    parser = argparse.ArgumentParser(description='This program copies selected DICOM files from 1 directory to another',
                                     prog='DICOM filter copy at MCB, UJ',
                                     usage='python filter_copy.py -input /some/path -output /other/path ',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-input', help='Path to folder with folders and files', required=True)
    parser.add_argument('-output', help='Output path', required=True)
    parser.add_argument('-date', help='Search files created on date (YYMMDD); Default is current date', default=date_pacs_format)

    args = parser.parse_args()
    # print(args.date)
    # dataPaths = directory.getChildrenPaths(date_pacs_format)

if __name__ == "__main__":
    main()