__author__ = 'jkordish'
'''Take a txt file that includes just CVEs and grab more details from cvedetails'''


import csv
import urllib2
from bs4 import BeautifulSoup

ifile = open('data/CVE.txt', "r").readlines()
ofile = writer = csv.writer(open('data/export.csv', 'wb'))

data = []
i = 0

for row in ifile:
    try:
        i = i + 1
        print((i, row.strip()))
        url = 'http://www.cvedetails.com/cve/'+row
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        CVE = soup.find(attrs={"name":"description"})['content'].split(':', 1)
        CVSS = soup.find('div', attrs={'class' : 'cvssbox'})
        data.append((CVE[0].strip(), CVE[1].lstrip(), CVSS.contents[0]))
    except:
        data.append((row.strip(), 'UNKNOWN CVE'))
        pass

writer.writerow(['CVE','Detail', 'CVSS'])
for row in data:
    ofile.writerow(row)