#!/usr/bin/python2
""" Small script to take in a Saint detailed csv and a Nessus csv and merged them together for pci purposes...
"""
__author__ = 'jkordish'

import sys
import csv
from optparse import OptionParser


def main():
    """main function"""
    cliOptions()


def cliOptions():
    """Take in user input for the paths of the saint/nessus csv files"""
    parser = OptionParser()

    parser.add_option("-s", "--saint", help="Please provide the Saint CSV file", dest="saint")
    parser.add_option("-n", "--nessus", help="Please provide the Nessus CSV file", dest="nessus")
    parser.add_option("-e", "--export", help="Please provide an name for export", dest="export")

    (options, args) = parser.parse_args()

    # hard coding the path to the csv files until i get the results I want and for simple testing.
    # you can remove/comment out the next two lines and invoke the python script with the flags above.
    #options.saint = 'data/saint.csv'
    #options.nessus = 'data/nessus.csv'
    #options.export = 'data/export.csv'

    # Ensure the Saint/Nessus csv files have been provided
    if options.saint is None or options.nessus is None:
        print 'Forgot the CSV reports'
        sys.exit(2)

    # Call Merged Results
    MergedResults(options.saint, options.nessus, options.export)


def SaintImport(saintcsv):
    """SaintImport: takes in a Saint CSV file and parses out HOST/CVE"""

    #Create a Dictionary for the HostName/CVE based key/value collection
    SaintList = []

    # Best to use the Saint PCI Details CSV Report
    SaintReport = csv.DictReader(open(saintcsv, 'rb'), delimiter=',',
                                 fieldnames=(
                                     'HostName', 'Vuln_Service', 'Class', 'CVE', 'CVSS', 'PCI_Compliant',
                                     'PCI_Severity', 'Unused'))

    # Example Output
    # Host Name,Vulnerability / Service,Class,CVE,CVSSv2 Base Score,PCI Compliant?,PCI Severity,
    # cisco1700.lab.ttc,Possible vulnerability in Cisco IOS 12.4(25a),Networking/SNMP,CVE-2010-0580,10.0,FAIL,high,

    # DictReader skips blank lines by default. Saint puts in a 7 line header with 3 blank lines. So skip 4
    SaintReport.next()
    SaintReport.next()
    SaintReport.next()
    SaintReport.next()

    # Iterate through SaintReport
    for row in SaintReport:
        # Grab row if row doesn't have a CVE but a CVSS over 3.9 - OR row has a CVSS of 3.9
        if (row['CVE'] is not '' and row['CVSS'] > '3.9') or (row['CVSS'] > '3.9'):
            #Append to our list
            SaintList.append(
                [
                    row['HostName'],
                    row['CVE'],
                    row['CVSS'],
                    row['PCI_Severity'],
                    row['Vuln_Service'],
                    'Saint'
                ]
            )
    return SaintList


def NessusImport(nessuscsv):
    """NessusImport: takes in a Nessus CSV file and parses out HOST/CVE"""

    #Create a Dictionary for the HostName/CVE based key/value collection
    NessusList = []

    # Read in Nessus CSV file using DictReader
    NessusReport = csv.DictReader(open(nessuscsv, 'rb'), delimiter=',',
                                  fieldnames=(
                                      'PluginID', 'CVE', 'CVSS', 'Risk', 'Host', 'Protocol', 'Port', 'Name', 'Synopsis',
                                      'Description',
                                      'Solution', 'PluginOutput'))

    # Example Output
    #Plugin ID,CVE,CVSS,Risk,Host,Protocol,Port,Name,Synopsis,Description,Solution,Plugin Output
    #"10068","CVE-1999-0612","5.0","Medium","10.120.10.223","tcp","79","Finger Service Remote Information
    # Disclosure","It is possible to obtain information about the remote host.","The remote host is running the
    # 'finger' service.

    # Skips the top header
    NessusReport.next()

    # Iterate through NessusReport (the csv file)
    for row in NessusReport:
        # Grab row if row doesn't have a CVE but a CVSS over 3.9 - OR row has a CVSS of 3.9
        if (row['CVE'] is not '' and row['CVSS'] > '3.9') or (row['CVSS'] > '3.9'):
            # Append to our list
            NessusList.append(
                [
                    row['Host'],
                    row['CVE'],
                    row['CVSS'],
                    row['Risk'],
                    row['Name'],
                    'Nessus'
                ]
            )
    return NessusList


def MergedResults(saintcsv, nessuscsv, exportcsv):
    """MergeResults: Merge Saint and Nessus"""

    # Set saint variable by using the results from SaintImport
    saint = SaintImport(saintcsv)
    # Set nessus variable by using the results from NessusImport
    nessus = NessusImport(nessuscsv)

    # A List to store our merged results.
    merged = []

    # Combine saint/nessus lists then sort it. Each row append to the merged list
    for row in list(sorted(saint + nessus)):
        merged.append(row)

    # If export flag was not set then print other wise call cvsExport
    if exportcsv is None:
        for row in merged:
            print(row)
    else:
        csvExport(exportcsv, merged)


def csvExport(export, data):
    """csvExport: export merged data into a csv"""

    # Create the CSV per the -e flag in cliOptions()
    writer = csv.writer(open(export, 'wb'))
    # Header
    writer.writerow(['Host', 'CVE', 'CVSS', 'Severity', 'Detail'])
    # Enumerate data and write each row to the csv file
    for row in sorted(data):
        writer.writerow(row)

if __name__ == '__main__':
    main()