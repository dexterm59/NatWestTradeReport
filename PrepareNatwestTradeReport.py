import csv
import datetime
from datetime import datetime
from datetime import timedelta
from datetime import date
import argparse
import logging
import os.path

report_time = datetime.now()
report_extension = report_time.strftime("%Y%m%d-%H%M%S")

parser = argparse.ArgumentParser(description='Test argument parser with filenames.')

parser.add_argument('--headerfile', help='supply full path of the NW header file')
parser.add_argument('--tradereport', help='supply full path of the new trade file')
parser.add_argument('--amendreport', help='supply full path of the amended trade file')
parser.add_argument('--combinedreport', help='supply full path of the combined trade file')
parser.add_argument('--outfile', help='supply full path of the output file')
parser.add_argument('--logfile', help='supply full path of the log file')
parser.add_argument('--loglevel', help='verbosity of log: INFO, DEBUG')

args = parser.parse_args()

defaultinputfolder = 'c:/Users/Public/Documents/FENICS/batch/'
defaultoutputfolder = 'c:/Users/Public/Documents/FENICS/batch/NWTosend'
defaultlogfolder = 'c:/Users/Public/Documents/FENICS/batch/'

if args.headerfile == None:
    headerfile = 'NatWestHeaders.csv'
else:
    headerfile = args.headerfile
if args.tradereport == None:
    tradereport = defaultinputfolder + 'PBExport-New.csv'
else:
    tradereport = args.tradereport
if args.amendreport == None:
    amendreport = defaultinputfolder + 'PBExport amendments.csv'
else:
    amendreport = args.amendreport
if args.combinedreport == None:
    combinedreport = defaultinputfolder + 'CombinedReport.csv'
else:
    combinedreport = args.combinedreport

if args.outfile == None:
    outfile = defaultoutputfolder + 'WMC-Trades-' + report_extension + '.csv'
else:
    outfile = args.outfile
if args.logfile == None:
    logfile = defaultlogfolder + 'TradeProc.log'
else:
    logfile = args.logfile
if args.loglevel == None:
    loglevel = 'DEBUG'
else:
    loglevel = args.loglevel

#avoid overwriting previous reports

combinedreport = os.path.splitext(combinedreport)[0] + report_extension + '.csv'

numeric_level = getattr(logging, loglevel.upper())

logging.basicConfig(filename=logfile, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=numeric_level)
logging.info("Trade Proc started")

logging.info("Script running with: headerfile: %s, tradereport: %s, outfile: %s, logfile: %s, loglevel: %s",
             headerfile, tradereport, outfile, logfile, loglevel)




logging.info("Opening header input file %s.", headerfile)
csvfile = open(headerfile, 'r')
sreader = csv.DictReader(csvfile)
# create hdr as a list and put all the field ids in it
hdr = []
for row in sreader:
    hdr.append(row['FieldID'])
headerstr = ','.join(hdr)
logging.info("Field header parsed: %s", headerstr)
csvfile.close()

# open automatically generated report file as a dictionary
logging.info("Opening trade input file %s.", tradereport)

#combine input files
#check on existence of new and amended trades files
#combine files for processing and write new temp file to avoid collisions

tfile_exists = os.path.isfile(tradereport)
afile_exists = os.path.isfile(amendreport)
cfile = open(combinedreport, 'w', newline='')

if tfile_exists:
    tktfile = open(tradereport, 'r', newline='')
    tktdata = tktfile.read()
    tktfile.close()
    os.rename(tradereport, os.path.splitext(tradereport)[0] + report_extension + '.csv')
    cfile.write(tktdata)
if afile_exists:
    afile = open(amendreport, 'r', newline='')
    adata = afile.read()
    afile.close()
    os.rename(amendreport, os.path.splitext(amendreport)[0] + report_extension + '.csv')
    cfile.write(adata)
cfile.close()
if tfile_exists == False & afile_exists == False:
    logging.info("No files to process. Exiting...")
    exit(0)
    

cfile = open(combinedreport, 'r', newline='')
treader = csv.DictReader(cfile, fieldnames=hdr)

logging.info("Opening output file %s.", outfile)
outputfile = open(outfile, 'w', newline='')
writer = csv.writer(outputfile, delimiter=',')
logging.debug("Writing hdr to output file: %s", hdr)
writer.writerow(hdr)
line = []
emptydatestr = '//'
datefields = ['fixing_date ',
              'option_expiry_date ',
              'option_premium_date ',
              'exotic_option_barrier_startdate',
              'option_settlement_date ',
              'exotic_option_barrier_startdate',
              'exotic_option_barrier_enddate',
              'exotic_option_lower_barrier_startdate',
              'exotic_option_lower_barrier_enddate',
              'exotic_option_upper_barrier_startdate',
              'exotic_option_upper_barrier_enddate']
new_trades = 0
amended_trades = 0;
for trow in treader:

    # fill in fixed fields

    trow['source_system'] = 'WMC-Source-System'
    trow['account '] = 'WMC-Account-ID'

    logging.info("Wrote fixed fields for source system_and account: %s, %s.", trow['source_system'],
                 trow['account '])

    # fix date fields
    for d in datefields:
        if trow[d] == emptydatestr:
            logging.debug("Replaced empty date string in field %s", d)
            trow[d] = ''

    # distinguish between spot and forward.  This should be more sophisticated
    # Initial version assumes that spot value date is less than or equal to 5 days from trade date

    if trow['contract_type_code '] == 'FXFW':
        tradedate = datetime.strptime(trow['trade_date '], '%d/%m/%Y')
        valuedate = datetime.strptime(trow['value_date '], '%d/%m/%Y')
        diff = valuedate - tradedate
        if diff.days <= 5:
            trow['contract_type_code '] = 'FXSP'
            logging.debug("Marked FXFW as Spot: value/trade date diff: %d", diff.days)
    if trow['amended_trade_flag '] == 'Y':
        amended_trades += 1
    else:
        new_trades += 1
            

    for key, value in trow.items():
        line.append(value)
    writer.writerow(line)
    logging.debug("Wrote line (list) to csv outfile: %s", line)
    
    del line[:]
logging.info("Processed %d new trades, %d amended trades", new_trades, amended_trades)

cfile.close()
os.remove(combinedreport)
outputfile.close()
