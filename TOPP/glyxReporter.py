def handle_args(argv=None):
    import argparse
    usage = "\nReporter for analysis file"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infileAnalysis",help="File input Analysis file .xml")
    parser.add_argument("--out", dest="outfile",help="File output xls file")
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options): 

    # parse analysis file
    fin = glyxsuite.io.GlyxXMLFile()
    fin.readFromFile(options.infileAnalysis) 

    # get features
    features = {}
    for feature in fin.features:
        features[feature.getId()] = feature

    # get hits
    data = {}
    comps = set()
    for h in fin.glycoModHits:
       
        feature = features[h.featureID]
        peptide = h.peptide
        glycan = h.glycan
        charge = feature.getCharge()
        
        # calculate theoretical glycopeptide mass
        mass = (peptide.mass+
                glycan.mass+
                glyxsuite.masses.MASS["H+"]*charge)/charge
        if abs(h.error) > 20*10**-6*(peptide.mass+glycan.mass):
            continue
        comp = glycan.composition
        comps.add(comp)
        seq = peptide.toString()
        if not seq in data:
            data[seq] = {}
        if not comp in data[seq]:
            data[seq][comp] = set()
        data[seq][comp].add("{}({})".format(str(round(mass,1)),str(charge)))

    # write output
    comps = sorted(list(comps))

    wb = xlwt.Workbook()
    ws0 = wb.add_sheet("Resultstable")

    # write header
    for col,comp in enumerate(["Peptides"]+comps):
        ws0.write(0,col,re.sub("[A-Z]+0","",comp))
    row = 0
    for seq in data:
        row += 1
        # write sequence
        ws0.write(row,0,seq)
        col = 0
        for comp in comps:
            col += 1
            if comp in data[seq]:
                ws0.write(row,col,";".join(data[seq][comp]))
                
    wb.save(options.outfile)


import sys
import glyxsuite
import xlwt
import re

if __name__ == "__main__":
    options = handle_args()
    main(options)
 