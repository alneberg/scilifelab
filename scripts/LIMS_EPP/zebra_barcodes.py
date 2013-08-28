#!/usr/bin/env python
import sys
from argparse import ArgumentParser
import subprocess

def construct(*args, **kwargs):
    start = int(kwargs.get('start'))
    end = int(kwargs.get('end'))
    
    for i in range(start, end):
        PID = "P"+str(i)
        makeProjectBarcode(PID)
    
def makeProjectBarcode(PID):
    print "^XA" #start of label
    print "^DFFORMAT^FS" #download and store format, name of format, end of field data (FS = field stop)
    print "^LH0,0" # label home position (label home = LH)
    print "^FO360,20^AFN,60,20^FN1^FS" #AF = assign font F, field number 1 (FN1), print text at position field origin (FO) rel. to home
    print "^FO140,5^BCN,70,N,N^FN2^FS" #BC=barcode 128, field number 2, Normal orientation, height 70, no interpreation line. 
    print "^XZ" #end format
    
    for i in range (1,6):
        PlateID="P"+str(i)
        plateCode=PID+PlateID
        print "^XA" #start of label format
        print "^XFFORMAT^FS" #label home posision
        print "^FN1^FD"+plateCode+"^FS" #this is readable
        print "^FN2^FD"+plateCode+"^FS" #this is the barcode
        print "^XZ"

def makeContainerBarcode(plateid,copies=1):
    lines = []
    lines.append("^XA") #start of label
    lines.append("^DFFORMAT^FS") #download and store format, name of format, end of field data (FS = field stop)
    lines.append("^LH0,0") # label home position (label home = LH)
    lines.append("^FO360,20^AFN,60,20^FN1^FS") #AF = assign font F, field number 1 (FN1), print text at position field origin (FO) rel. to home
    lines.append("^FO70,5^BCN,70,N,N^FN2^FS") #BC=barcode 128, field number 2, Normal orientation, height 70, no interpreation line. 
    lines.append("^XZ") #end format

    for copy in xrange(copies):
        lines.append("^XA") #start of label format
        lines.append("^XFFORMAT^FS") #label home posision
        lines.append("^FN1^FD"+plateid+"^FS") #this is readable
        lines.append("^FN2^FD"+plateid+"^FS") #this is the barcode
        lines.append("^XZ")
    return lines
    
def getArgs():
    description = ("Print barcodes on zebra barcode printer "
                   "for NGI Genomics Projects.")
    parser = ArgumentParser(description=description)
    parser.add_argument('--plateid',
                        help='The plate ID to print on the barcode.')
    parser.add_argument('--printout',action="store_true",
                        help=('Print file on default or '
                              'supplied printer using lp command.'))
    parser.add_argument('--hostname',
                        help='Hostname for lp CUPS server.')
    parser.add_argument('--destination',
                        help='Name of printer.')
    parser.add_argument('--copies', default=1, type=int,
                        help='Number of printout copies')
    return parser.parse_args()

def main(args):
    lines = []
    if args.plateid is not None:
        lines += makeContainerBarcode(args.plateid, copies=args.copies)
    if args.printout is None:
        print '\n'.join(lines)
    elif lines:
        lp_args = ["lp"]
        if args.hostname:
            lp_args += ["-h",args.hostname]
        if args.destination:
            lp_args += ["-d",args.destination]
        lp_args.append("-") # lp accepts stdin if '-' is given as filename
        print lp_args
        sp = subprocess.Popen(lp_args, stdin=subprocess.PIPE)
        sp.stdin.write(str('\n'.join(lines)))
        sp.stdin.close()

if __name__ == '__main__':
    arguments = getArgs()
    main(arguments)
