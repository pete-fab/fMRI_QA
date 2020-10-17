# fMRI_QA
fMRI_QA tool used in Małopolskie Centrum Biotechnologii, Jagiellonian University

Tool has the following prerequisit on the fp;der structure of DICOM files. The files inside working directory should be grouped inside folders named with study date. Inside there should be a folder named fBIRN containing phantom scan data according BIRN QA suggestions: http://www.birncommunity.org/tools-catalog/function-birn-stability-phantom-qa-procedures/

Features that will be added in due course:

1. Automatic restructuring of QA data based on DICOM tag values.  Package that could be used to accomplish this: https://github.com/suever/dicomSort or https://github.com/pete-fab/organize_DICOM
2. (possibly) Automatic pulling of required images from DICOM node. Python packages that could be used to accomplish this: http://docs.openrem.org/en/0.7.1/index.html, http://gdcm.sourceforge.net/html/pages.html
3. Automatic generation of interactive charts. Packages: https://plot.ly/python/, http://matplotlib.org/gallery.html, http://bokeh.pydata.org/en/latest/
4. Change how data is being compressed after the analysis.
                         
