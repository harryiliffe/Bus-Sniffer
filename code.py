import re
import mechanize
import hashlib
from bs4 import BeautifulSoup
from datetime import date,timedelta

locationTo = "Whanganui / Wanganui"
locationFrom = "Wellington - Central"
travelDateStart = date(2017,9,7)
travelDateEnd = date(2018,9,7)

busIndex = []
busIndexNum = 0
oneday = timedelta(1)
dayCount = 0
def Format(dateIn):
	return "%d-%s-%s" % (dateIn.year, str(dateIn.month).zfill(2), str(dateIn.day).zfill(2))

class Bus:
	def __init__(self,index,date,departs,arrives,price):	
		self.index = index
		self.date = date
		self.departure = departs
		self.arrival = arrives
		self.price = price

	def describe(self):
		print "Index: %d, Date: %s, Departure Time: %s, Arrivel Time: %s, Price: %s" % (self.index, self.date, self.departure, self.arrival, self.price)




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
			cost = soup.find('div', id="ResOpt_%d" % i).find("span", class_="PriceDef").find("label").text
			busIndex.append(Bus(busIndexNum, searchDate, departureTime, arrivalTime, cost))
			busIndex[busIndexNum].describe()
			busIndexNum += 1
			i+=1
		else:
			dayCount+=1
			break
