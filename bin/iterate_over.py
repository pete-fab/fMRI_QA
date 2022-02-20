import copy_physio_files

file1 = open('/data/NEUROSMOG/list.txt', 'r')
Lines = file1.readlines()
 
count = 0
# Strips the newline character
for line in Lines:
    count += 1
    print("Line{}: {}".format(count, line.strip()))
    copy_physio_files.copy_physio_files("/neurosmog/"+line.strip(),"/data/NEUROSMOG","NEUROSMOG")
    # copy_physio_files.copy_physio_files("/data/raw_with_physio\NEUROSMOG\CIESIELSKA_KAMILA_91037348","/data/debug","NEUROSMOG")
