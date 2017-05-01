import csv
import datetime
from datetime import datetime
from datetime import timedelta
from datetime import date
import argparse

parser = argparse.ArgumentParser(description='Test argument parser with filenames.')

parser.add_argument('--headerfile', help='supply full path of the NW header file')
parser.add_argument('--tradereport', help='supply full path of the input file')
parser.add_argument('--outfile', help='supply full path of the output file')
parser.add_argument('--logfile', help='supply full path of the log file')
parser.add_argument('--loglevel', help='verbosity of log: high or low')

args = parser.parse_args()

if args.headerfile == None:
          args.headerfile = 'NatWestHeaders.csv'
if args.tradereport == None:
          args.headerfile = 'PB-Export-New.csv'
if args.headerfile == None:
          args.headerfile = 'ProcessedReport.csv'



print("*********************************** New Run **************************************")
csvfile = open(args.headerfile, 'r')
sreader = csv.DictReader(csvfile)
#create hdr as a list and put all the field ids in it
hdr = []
for row in sreader:
          hdr.append(row['FieldID'])
headerstr = ','.join(hdr)
print(headerstr)
csvfile.close()


#open automatically generated report file as a dictionary
tktfile = open(args.tradereport, 'r', newline='')
treader = csv.DictReader(tktfile,fieldnames=hdr)
outputfile = open(args.outfile, 'w', newline='')
writer = csv.writer(outputfile, delimiter=',')
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

for trow in treader:

          #fill in fixed fields
          
          trow['source_system'] = 'WMC-Source-System'
          trow['account '] = 'WMC-Account-ID'

          #fix date fields
          for d in datefields:
                    if trow[d] == emptydatestr:
                              print("Found one  ", d)
                              trow[d] = ''

          #distinguish between spot and forward.  This should be more sophisticated
          #Initial version assumes that spot value date is less than or equal to 5 days from trade date
          
          if trow['contract_type_code '] == 'FXFW':
                    tradedate = datetime.strptime(trow['trade_date '], '%d/%m/%Y')
                    valuedate = datetime.strptime(trow['value_date '], '%d/%m/%Y')
                    diff = valuedate - tradedate
                    if diff.days <= 5:
                              trow['contract_type_code '] = 'FX'
                    
                    

          for key,value in trow.items():
                    line.append(value)
          writer.writerow(line)
          del line[:]
tktfile.close()
outputfile.close()
