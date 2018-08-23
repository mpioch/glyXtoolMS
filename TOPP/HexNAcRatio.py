# Tool for calculating peptide scores for HCD and ETD fragments

import glyxtoolms
import sys 


def handle_args(argv=None):
    import argparse
    usage = "\nFile HexNAcRatio\n Calculates the ratio between HexNAc1-H2O(+) and HexNAc1(1+) fragment ions of each identification"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file with annotated fragments.xml") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with filtered glycans")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args



def main(options):
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)
    glyML.addToolValueDefault("HexNAcRatio", 0.0)
    for h in glyML.glycoModHits:
        fHexNAc = h.fragments.get("HexNAc1(1+)",None)
        fHexNAcH2O = h.fragments.get("HexNAc1-H2O(+)",None)
        if fHexNAc == None:
            continue
        if fHexNAcH2O == None:
            continue
        value = fHexNAcH2O.peak.y/fHexNAc.peak.y
        h.toolValues["HexNAcRatio"] = round(value,3)
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
