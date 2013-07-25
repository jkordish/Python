#!/usr/bin/python2

###
#
# Python script to massage a Saint CSV report into something useable
# The output would be something you can use to import directly into
# a Redmine ticketing system using the Redmine_Import plugin.
#    - https://github.com/leovitch/redmine_importer
#
# NOT SUITABLE FOR PUBLIC RELEASE
#
###


import sys
import csv


writer = csv.writer(open('export.csv', 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

dataMundge = []
# Open up the CSV using the first argument passed
#TODO: move report.csv back to sys.argv[1]
saintReport = csv.DictReader(open(sys.argv[1], 'rb'), delimiter=',',
        fieldnames=('HOST', 'VULN', 'CLASS', 'CVE', 'CVSS', 'COMPLIANT', 'SEVERITY', 'UNUSED'))

next(saintReport)
next(saintReport)
next(saintReport)
next(saintReport)

for row in saintReport:
    for key, value in row.items():
        if value == 'FAIL':
            dataMundge.append(row.items())

writer.writerow(['Subject', 'Description', 'Author', 'Tracker'])
#TODO: Add some more data in here like project/customer/etc. populate more fields
for entry in dataMundge:
    writer.writerow( [(entry[5][1]) + " " + (entry[4][1])] +
            [(entry[4][0]) + ": " + (entry[4][1]) + " " + (entry[6][0]) + ": " + (entry[6][1]) + " " + (entry[7][0]) + ": " + (entry[7][1])] +
            ['admin'] +
            ['Findings'])
