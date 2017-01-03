DATA_DIR = '/media/sf_MAGAZYN/Data/QA/QA_fMRI_data/'
PACS_DIR = '/home/brain/Documents/test_DICOM_storage/'
DICOMSERVER_DIR = PACS_DIR
DICOMSERVER_AET = 'PYNETDICOM'
DICOMSERVER_PORT = 9999
DATA_REQUESTINGPHYSICIAN = "fMRI"
DATA_SERIESDESCRIPTION = "fBIRN_epi"
DATA_REFERRINGPHYSICIANNAME = "QA"
DATA_EXT = "dcm"
SLICE_RANGE = xrange(3, 30, 3)
ATTRIBUTE_LIST = ['percentFluc', 'drift', 'driftfit',
                  'mean', 'SNR', 'SFNR',
                  'rdc',
                  'minFWHMX', 'meanFWHMX', 'maxFWHMX',
                  'minFWHMY', 'meanFWHMY', 'maxFWHMY',
                  'minFWHMZ', 'meanFWHMZ', 'maxFWHMZ',
                  'dispCMassX', 'driftCMassX', 'dispCMassY',
                  'driftCMassY', 'dispCMassZ', 'driftCMassZ',
                  'meanGhost', 'meanBrightGhost']
ALL_LOG = 'all.log'
RUNTIME_LOG = '.runtime.rlog'
RUNTIME_START = 'qa_script_start'
RUNTIME_STOP = 'qa_script_stop'

IS_SAVE_ANALYSIS_FILES = True
IS_SAVE_ORIGINAL_FILES = True

IS_DEBUG = True
DEBUG_DIR = '/media/sf_MAGAZYN/Data/QA/QA_fMRI_debug/'
SLICE_RANGE_DEBUG = xrange(15, 18, 5)
ATTRIBUTE_LIST_DEBUG = ['percentFluc', 'drift', 'SNR', 'SFNR']

GLOBAL_SUMMARY_FILE = 'global_summary.csv'
LOCAL_SUMMARY_FILE = 'local_summary.csv'

PLOTS = { 1: {
              'attributes': ['percentFluc', 'drift', 'driftfit'],
              'range': [],
              'title': "Drift related parameters",
              'ytitle': "Arbitrary unit"
          },
          2: {
              'attributes': ['mean', 'SNR', 'SFNR'],
              'range': [],
              'title': "Signal quality related parameters",
              'ytitle': "Arbitrary unit"
          },
          3: {
              'attributes': ['rdc'],
              'range': [],
              'title': "Radius of decorelation",
              'ytitle': "pixels"
          },
          4: {
              'attributes': ['meanFWHMX', 'meanFWHMY', 'meanFWHMZ'],
              'range': [('FWHMX','minFWHMX', 'maxFWHMX'),('FWHMY','minFWHMY',  'maxFWHMY'), ('FWHMZ','minFWHMZ', 'maxFWHMZ')],
              'title': "Full Width Half Maximum",
              'subplots': [(1, 1), (2, 1), (3, 1)],
              'ytitle': "milimeters"
          },
          5: {
              'attributes': ['dispCMassX', 'driftCMassX', 'dispCMassY',
                            'driftCMassY', 'dispCMassZ', 'driftCMassZ'],
              'range': [],
              'title': "Phantom perceived displacement",
              'ytitle': "milimeters"
          },
          6: {
              'attributes': ['meanGhost', 'meanBrightGhost'],
              'range':(),
              'title': "Ghost value",
              'ytitle': "Arbitrary unit"
          }
}


