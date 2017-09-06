import re, os.path, mechanize, csv
from bs4 import BeautifulSoup
from datetime import date,timedelta
from collections import deque

startFresh = True
# locationFrom = "Whanganui / Wanganui"
locationTo = "Rotorua"
locationFrom = "Wellington - Central"
travelDateStart = date(2017,10,20)

travelDateEnd = date(2018,9,7)

filename = "csv/IC:%s - %s.csv" % (locationFrom.replace("/","_"), locationTo.replace("/","_"))
filenameOfInterest = "csv/IC:%s - %s - CHEAPAF.csv" % (locationFrom.replace("/","_"), locationTo.replace("/","_"))

busIndex = []
busIndexNum = 0
oneday = timedelta(1)
dayCount = 0
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
busOfInterest = []



def Format(dateIn):
	return "%d-%s-%s" % (dateIn.year, str(dateIn.month).zfill(2), str(dateIn.day).zfill(2))
def ParseDate(dateIn):
	year,month,day = re.split("-", dateIn)
	return date(int(year),int(month),int(day))

class Bus:
	def __init__(self,index,date,weekday,departs,arrives,price):	
		self.index = index
		self.date = date
		self.weekday = weekday	
		self.departure = departs
		self.arrival = arrives
		self.price = price

		f = open(filename, 'a')
		try:
		    writer = csv.writer(f)
		    writer.writerow((self.index, self.date, days[self.weekday], self.departure, self.arrival, self.price))
		finally:
		    f.close()
	def describe(self):
		print "Index: %d, Date: %s, Weekday: %s, Departure Time: %s, Arrivel Time: %s, Price: %s" % (self.index, self.date, days[self.weekday], self.departure, self.arrival, self.price)
	
	def cost(self):
		if self.price != "SOLD OUT":
			return int(self.price.replace("$", ""))
		else:
			return 1000
	def ofInterest(self):
		f = open(filenameOfInterest, 'a')
		try:
		    writer = csv.writer(f)
		    writer.writerow((self.index, self.date, days[self.weekday], self.departure, self.arrival, self.price))
		finally:
		    f.close()



if not os.path.isfile(filename) or startFresh:
	f = open(filename, 'w')
	try:
	    writer = csv.writer(f)
	    writer.writerow( ("Index", "Date", "Weekday", "Departure Time", "Arrivel Time", "Price") )
	finally:
	    f.close()
	f = open(filenameOfInterest, 'w')
	try:
	    writer = csv.writer(f)
	    writer.writerow( ("Index", "Date", "Weekday", "Departure Time", "Arrivel Time", "Price") )
	finally:
	    f.close()
elif not startFresh: 
	with open(filename, 'r') as f:
	    try:
	        lastrow = deque(csv.reader(f), 1)[0]
	    except IndexError:  # empty file
	        lastrow = None
	    travelDateStart = ParseDate(lastrow[1]) + oneday
else:
	print "couldn't find file :("
	quit()


url = "http://www.intercity.co.nz"
br = mechanize.Browser()
response = br.open(url)
br.form = list(br.forms())[0]



while True:

	searchDate = travelDateStart + (oneday*dayCount)
	searchDateFormated = Format(searchDate)

	br.form = list(br.forms())[0]
	br["To"] = locationTo
	br["From"] = locationFrom
	br["Date_Travel"] = searchDateFormated
	# br["OneWayOrReturn"] = "OneWay"

	response2 = br.submit()
	# print response.read()
	htmlbody = response2.read()

	soup = BeautifulSoup(htmlbody, "lxml")



	i = 1
	while True:
		if soup.find('div', id="ResOpt_%d" % i) != None:
			
			departureTime = soup.find('div', id="ResOpt_%d" % i).find("span", class_="Departs").text
			arrivalTime = soup.find('div', id="ResOpt_%d" % i).find("span", class_="Arrives").text

			try:
				cost = soup.find('div', id="ResOpt_%d" % i).find("span", class_="PriceDef").find("label").text
			except Exception:
				cost = "SOLD OUT"

			busIndex.append(Bus(busIndexNum, searchDate, searchDate.weekday(), departureTime, arrivalTime, cost))
			busIndex[busIndexNum].describe()
			if busIndex[busIndexNum].cost() < 3:
				print "Found Cheap Bus"
				busOfInterest.append(busIndexNum)
				busIndex[busIndexNum].ofInterest()
			busIndexNum += 1
			i+=1
		else:
			dayCount+=1
			break
