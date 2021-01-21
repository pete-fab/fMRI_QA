# fMRI_QA
fMRI_QA tool used in Małopolskie Centrum Biotechnologii, Jagiellonian University

Tool has the following prerequisit on the fp;der structure of DICOM files. The files inside working directory should be grouped inside folders named with study date. Inside there should be a folder named fBIRN containing phantom scan data according BIRN QA suggestions: http://www.birncommunity.org/tools-catalog/function-birn-stability-phantom-qa-procedures/

## How to use

Obtain docker file locally:
```
make pull
```

To see the available options run
```
docker run -it neuromcb/fmri_qa:latest -h
```
Other parameters that can be modified are stored in `config.py`.

To run **single** analysis on default parameters, map your local drive into the docker container:
```
docker run -it -v "C:\Data":/data neuromcb/fmri_qa:latest -mode single -input /data/some_folder/ -output /data/some_other_folder/
```

To run **multi** analysis on default parameters:
```
docker run -it -v "C:\Data":/data neuromcb/fmri_qa:latest -mode single -input /data/some_folder/ -output /data/some_other_folder/
```

## Mode description

* `single` mode will only generate tabular results (csv file)
* `multi` mode will generate tabular results and graphs. The gtaphs generated in the `-output` folder. To see full reports follow: `output/graphs/plotly_dashboard/index.html`

                         
