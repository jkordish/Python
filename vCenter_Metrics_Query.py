#!/usr/bin/python

################################################################################
#
# Python Script File
#
# NAME:  vCenter_Metrics_Query.py  Version 1.5
#
# AUTHOR:  Joseph Kordish
# DATE  : 2/3/2011
#
# PURPOSE:  Query the vCenter Database and pull VirtualMachine statistics
#
#
# BUGS AND WORKAROUNDS: Requires the Database to be collecting extra metrics
# You define the statistical level for each historical interval in the 
# vSphere Client under <Administration><vCenter Server Settings><Statistics>
# Levels 4 4 2 2 have been found to be ideal
#
################################################################################

import sys
import os
import pyodbc
import subprocess
import base64
from optparse import OptionParser

logfile = '/var/log/vCenter_Metrics_Query.log'

parser = OptionParser()

parser.add_option("-u", "--username", help="Username to connect to the vCenter Database",           dest="username")
parser.add_option("-p", "--password", help="Password to connect to the vCenter Database",           dest="password")
parser.add_option("-d", "--debug",    help="Debug mode: check /var/log/vCenter_Metrics_Query.log",  dest="debug", action="store_true")

(options, args) = parser.parse_args()

if options.password is None or options.username is None:
	print 'ERROR: Both username and password are required arguments'
	sys.exit(2)
if options.debug is True:
	print 'Debug mode enabled. Check %s for output' % (logfile)
	output = open(logfile, 'w')

## Open a Connection to the database
cnxn = pyodbc.connect("Driver=TDS;Servername=vCenter;UID=%s;PWD=%s;" % (options.username, base64.decodestring(options.password)))
cursor = cnxn.cursor()

# query the vCenter for virtual machine cpu usage
def vcpu():
	rows = list(cursor.execute("""
SET NOCOUNT ON
select cast(vms.NAME as text) as 'VM',
cast(STAT_VALUE / 100 as decimal(9,2)) as 'CPU' from dbo.VPXV_HIST_STAT_DAILY
join VPXV_VMS vms
on substring(ENTITY,4,4)=vms.VMID
where (ENTITY like 'vm%')
and (SAMPLE_TIME>dateadd(mi,-45,getdate()))
and (STAT_NAME='usage')
and (STAT_GROUP='cpu')
and (STAT_ROLLUP_TYPE='average')
order by NAME, SAMPLE_TIME DESC
	"""))
	print 'Returning cpu rows'
	vmname = None
	for row in rows:
		if options.debug is True:
			output.write('Querying virtual machine cpu metrics\n')
			output.write('/opt/OV/bin/opcmon FLED_VirtualMachine_CPU=%s -object "Perf" -option NODE="%s"\n' % (row.CPU, row.VM))
		if vmname != row.VM:
			os.system('"/opt/OV/bin/opcmon" FLED_VirtualMachine_CPU=%s -object "Perf" -option NODE="%s"' % (row.CPU, row.VM))
			vmname = row.VM

# query the vCenter for virtual machine memory usage
def vmem():
	rows = list(cursor.execute("""
SET NOCOUNT ON
select cast(vms.NAME as text) as 'VM',
cast(STAT_VALUE / 100 as decimal(9,2)) as 'MEM' from dbo.VPXV_HIST_STAT_DAILY
join VPXV_VMS vms
on substring(ENTITY,4,4)=vms.VMID
where (ENTITY like 'vm%')
and (SAMPLE_TIME>dateadd(mi,-45,getdate()))
and (STAT_NAME='usage')
and (STAT_GROUP='mem')
and (STAT_ROLLUP_TYPE='average')
order by NAME, SAMPLE_TIME DESC
	"""))
	print 'Returning memory rows'
	vmname = None
	for row in rows:
		if options.debug is True:
			output.write('Querying virtual machine memory metrics\n')
			output.write('/opt/OV/bin/opcmon FLED_VirtualMachine_MEM=%s -object "Perf" -option NODE="%s"\n' % (row.MEM, row.VM))
		if vmname != row.VM:
			os.system('"/opt/OV/bin/opcmon" FLED_VirtualMachine_MEM=%s -object "Perf" -option NODE="%s"' % (row.MEM, row.VM))
			vmname = row.VM

# query the vCenter for the virtual machine vmdk free space
def vdsk():
	rows = list(cursor.execute("""
SET NOCOUNT ON
select
e.NAME as 'VM',
100 - (100 * cast(g.FREE_SPACE as bigint) / cast(g.CAPACITY as bigint)) as 'FREE', PATH
from dbo.VPX_GUEST_DISK as g left join dbo.VPX_ENTITY as e
on g.VM_ID = e.ID
Order by VM
	"""))
	print 'Returning disk free rows'
	for row in rows:
		path = str(row.PATH)
		path = path.rstrip('\:\\')
		if options.debug is True:
			output.write('Querying virtual machine disk space metrics\n')
			output.write('/opt/OV/bin/opcmon FLED_VirtualMachine_DISKFREE=%s -object "Perf" -option NODE="%s" -option PATH="%s"\n' % (row.FREE, row.VM, path))
		os.system('"/opt/OV/bin/opcmon" FLED_VirtualMachine_DISKFREE=%s -object "Perf" -option NODE="%s" -option PATH="%s"' % (row.FREE, row.VM, path))

# query the vCenter for the virtual machine cpu wait metric
def cpuwait():
	rows = list(cursor.execute("""
SET NOCOUNT ON
select cast(vms.NAME as text) as 'VM',
STAT_VALUE as 'WAIT' from dbo.VPXV_HIST_STAT_DAILY
join VPXV_VMS vms
on substring(ENTITY,4,4)=vms.VMID
where (ENTITY like 'vm%')
and (SAMPLE_TIME>dateadd(mi,-45,getdate()))
and (STAT_NAME='wait')
and (STAT_GROUP='cpu')
order by NAME, SAMPLE_TIME DESC
	"""))
	print 'Returning cpu wait rows'
	vmname = None
	for row in rows:
		if options.debug is True:
			output.write('Querying virtual machine cpu wait metrics\n')
			output.write('/opt/OV/bin/opcmon FLED_VirtualMachine_CPUWAIT=%s -object "Perf" -option NODE="%s"\n' % (row.WAIT, row.VM))
		if vmname != row.VM:
			os.system('"/opt/OV/bin/opcmon" FLED_VirtualMachine_CPUWAIT=%s -object "Perf" -option NODE="%s"' % (row.WAIT, row.VM))
			vmname = row.VM

# query the vCenter for the virtual machine vmdk disk io metric
def diskio():
	rows = list(cursor.execute("""
SET NOCOUNT ON
select cast(vms.NAME as text) as 'VM',
STAT_VALUE as 'IO' from dbo.VPXV_HIST_STAT_DAILY
join VPXV_VMS vms
on substring(ENTITY,4,4)=vms.VMID
where (ENTITY like 'vm%')
and (SAMPLE_TIME>dateadd(mi,-45,getdate()))
and (STAT_NAME='usage')
and (STAT_GROUP='disk')
and (STAT_ROLLUP_TYPE='average')
order by NAME, SAMPLE_TIME DESC
	"""))
	print 'Returning disk io rows'
	vmname = None
	for row in rows:
		if options.debug is True:
			output.write('Querying virtual machine disk io metrics\n')
			output.write('/opt/OV/bin/opcmon FLED_VirtualMachine_DISKIO=%s -object "Perf" -option NODE="%s"\n' % (row.IO, row.VM))
		if vmname != row.VM:
			os.system('"/opt/OV/bin/opcmon" FLED_VirtualMachine_DISKIO=%s -object "Perf" -option NODE="%s"' % (row.IO, row.VM))
			vmname = row.VM

## Call the methods
vcpu()
vmem()
vdsk()
cpuwait()
diskio()
