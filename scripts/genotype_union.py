#!/usr/bin/env python3

'''sdfsd

'''

# at some point, stop using print statements to log and use an actual logging framework.

import sys
import re
import csv
import argparse
import datetime

# global variables:
# VCF structure (used instead of index numbers for readability)
chrom = 0
pos = 1
snpID = 2
ref = 3
alt = 4
qual = 5
filt = 6
info = 7
frmt = 8


############################################# Functions #############################################

def get_args():
    '''Handle command line arguments (input and output file names).'''
    parser = argparse.ArgumentParser(description='Takes VCF file with samples that have been called by two callers and returns a VCF file where the genotypes from each caller are combined.')
    parser.add_argument('infile', help='Input VCF file name')
    parser.add_argument('outfile', help='Output VCF file name')
    results = parser.parse_args()
    return results.infile, results.outfile


def check_file(fname):
    '''Check that file can be read; exit with error message if not.'''
    try:
        f = open(fname, 'rb')
        f.close()
        return 0
    except IOError:
        print('ERROR: Could not read file', fname)
        return 1
        sys.exit()
    f.close()


def get_header(infile):
    '''Extract header from VCF.
    Exit with error message if no header detected.
    '''
    headerCheck = 1
    with open(infile, 'r') as file:
        for line in csv.reader(file, delimiter='\t'):
            if "#CHROM" in line:
                headerCheck = vcf_check(line)
                return line
        if headerCheck == 1:
            print("ERROR: File must contain header row matching VCF specification")
            return 1
            sys.exit()


def vcf_check(line):
    '''Rudimentary format check.
    Must have #CHROM-designated header row and >=2 genotype columns.
    Must have an even number of genotype columns (does not actually
    check pairing).
    '''
    if ((len(line) % 2) == 0) or len(line) < 11:
        print('ERROR: Unpaired sample names detected.  File must contain an even number of samples.')
        return 1
        sys.exit()
        # note that there should be an ODD number of columns (9 + even number of samples)
    else:
        return 0


def evaluate_variant_line(line, start1, end1, start2, end2):
    '''For non-header lines, determines what needs to be done
    do merge the genotype information:
        1. Add set annotation (HC, DV, HC-DV) to INFO
        2. Removes empty genotypes for variants called by one caller
        3. Removes chr_pos_ref_alt from ID field for DV-only variants
        4. Integrates info for variants called by both
    '''
    if (':DV_' in line[frmt]) and not (':HC_' in line[frmt]):
        line = add_set_tag('DV', line)
        line = remove_empty_genotypes(line, start1, end1, start2, end2)
        line[snpID] = '.'
        return line
    elif (':HC_' in line[frmt]) and not (':DV_' in line[frmt]):
        line = add_set_tag('HC', line)
        line = remove_empty_genotypes(line, start1, end1, start2, end2)
        return line
    elif (':DV_' in line[frmt]) and (':HC_' in line[frmt]):
        line = add_set_tag('HC-DV', line)
        line = combine_genotypes(line, start1, end1, start2, end2)
        line[snpID] = '.'
        return line
    else:
        print('ERROR: Neither caller annotation found in FORMAT field.')
        return 1
        sys.exit()


def find_genotype_indices(line):
    '''Determines the start/stop point for genotype columns from the two callers.
    bcftools merge --force-samples results in a VCF with samples as so:
        chr pos ... sample1 sample2 2:sample1 2:sample2, where the first
        two columns are called with caller1 and the second two with caller2.
    This function determines the index numbers defining these two ranges
    (assuming the columns are not inter-mingled, e.g. sample1 2:sample1 2:sample2 sample2).

    Bear in mind that python slicing [start:stop] gets items start to stop-1.
    Example: vcf with 6 genotype fields at indices 9-14: 0,1,...8,9,10,11,12,13,14
        see inline comments working through this example.
    '''
    start1 = 9                      # start1=9; index=9 field
    end2 = len(line)                # end2=15; index=15-1=14 field
    end1 = int(9 + (end2 - 9)/2)         # end1=9+(15-9)/2=12, [9:12] gets indices 9,10,11 (and not 12,13,14)
    start2 = end1                   # start2=12; [12:15] gets indices 12,13,14
    return start1, end1, start2, end2


def add_set_tag(caller, line):
    '''Add set (HC, DV, HC-DV) to INFO fields.'''
    line[info] = line[info] + ';set=' + caller
    return line


def remove_empty_genotypes(line, start1, end1, start2, end2):
    '''For variants found by only one caller, remove empty (.:.:.) fields.'''
    if any('0' in s for s in line[start1:end1]):
        line = line[0:end1]
        return line
    elif any('0' in s for s in line[start2:end2]):
        line = line[0:9] + line[start2:end2]
        return line
    else:
        print('ERROR: All genotype fields are blank.')
        return 1
        sys.exit()


def combine_genotypes(line, start1, end1, start2, end2):
    '''For variants found by both callers, integrate genotype info.
    Variants called by both callers will look like this:
        sample1          2:sample1
        0/1:3:4,5:.:.:.  .:.:.:0/1:2:4,3
    We want the union of this information, e.g.:
        sample1
        0/1:3:4,5:0/1:2:4,3
    This function compares the two genotype fields sample1 and 2:sample1,
    and anywhere there's a '.' in sample1, it updates it with non-'.'
    data from 2:sample1 if available.  This assumes that the VCF is well-formed,
    meaning each genotype column conforms equally to the FORMAT definition.

    This function also updates the GT column.  If the DV_GT and HC_GT fields
    are concordant, GT stays the same; otherwise, GT is set to ./.
    '''

    for x, y in zip(line[start1:end1], line[start2:end2]):
        geno1 = x.split(':')
        geno2 = y.split(':')
        field = line.index(x)
        for i, g1 in enumerate(geno1):
            if i == 0:
                if geno1[i] != geno2[i]:
                    geno1[i] = './.'
            if (geno1[i] == '.') and (geno2[i] != '.'):
                geno1[i] = geno2[i]
        line[field] = ':'.join(geno1)

    return line[0:end1]


def add_headers(ts, ver, scriptName, cmdString):
    '''Add metadata to the vcf
    To A) account for new INFO field and to B) document provenance.
    '''
    infoHeader = '##INFO=<ID=set,Number=3,Type=String,Description="Set of callers that identified a variant (HC, DV, or HC-DV)">'
    prov1 = '##' + scriptName + '_Version=' + ver + ', Union of HC and DV genotype data, ' + ts
    prov2 = '##' + scriptName + '_Command=' + cmdString
    return [infoHeader, prov1, prov2]


#####################################################################################################


if __name__ == '__main__':
    ts = str(datetime.datetime.now())
    ver = 'someversion' # https://stackoverflow.com/questions/5581722/how-can-i-rewrite-python-version-with-git
    scriptName = sys.argv[0]
    cmdString = ' '.join(sys.argv)
    infile, outfile = get_args()
    check_file(infile) 
    headerLine = get_header(infile)
    start1, end1, start2, end2 = find_genotype_indices(headerLine)
    with open(infile, 'r') as file, open(outfile, 'w') as out:
        for line in csv.reader(file, delimiter='\t'):
            if re.search(r'#', line[chrom]) is None:
                line = evaluate_variant_line(line, start1, end1, start2, end2)
                out.write('\t'.join(line) + '\n')
            elif "#CHROM" in line:
                out.write('\n'.join(add_headers(ts, ver, scriptName, cmdString)) + '\n')
                out.write('\t'.join(line) + '\n')
            else:
                out.write('\t'.join(line) + '\n')
        
            
