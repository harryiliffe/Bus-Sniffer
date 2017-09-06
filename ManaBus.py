import re, os.path, mechanize, csv
from bs4 import BeautifulSoup
from datetime import date,timedelta
from collections import deque

import requests


locationTo = "Palmerston North"
locationFrom = "Wellington - Central"

locationDict = {'Hastings': '218', 'Wairakei': '225', 'Auckland': '191', 'Kaiwaka': '310', 'Whitianga': '292', 'Whenuakite': '548', 'Oakleigh': '308', 'Bay View': '704', 'Whangarei - Kamo': '554', 'Tairua': '293', 'Akoranga ( North Shore Auckland )': '553', 'Mangatawhiri': '431', 'Te Pohue': '695', 'Towai': '560', 'Pokeno': '1000163', 'Wellsford': '307', 'Paeroa': '428', 'Whangarei': '309', 'Ngaruawahia': '228', 'Hamilton - Central': '193', 'Ngatea': '429', 'Albany ( North Shore Auckland )': '304', 'Hamilton - Waikato University': '449', 'Manukau ( Auckland )': '192', 'Maramarua': '430', 'Warkworth': '306', 'Bulls': '299', 'Mount Maunganui ( Tauranga )': '291', 'Napier': '220', 'Karapiro': '241', 'Auckland Airport - Int Terminal': '536', 'Taihape': '234', 'Massey University (Palmerston Nth)': '256', 'Tauranga (Central)': '229', 'Matamata': '231', 'Reporoa': '745', 'Hot Water Beach': '551', 'Palmerston North': '240', 'Auckland Airport - Domestic Terminal': '534', 'Kawakawa': '562', 'Paihia - Bay of Islands': '558', 'Clive': '246', 'Rotorua': '194', 'Hikuai': '300', 'Taupo': '224', 'Opua Hill': '631', 'Thames': '294', 'Morrinsville-Tatuanui': '697', 'Waihi': '301', 'Brynderwyn': '311', 'Ruakaka': '313', 'Wellington - Central': '196', 'Bayfair ( Tauranga )': '290', 'Coroglen': '552', 'Morrinsville': '696', 'Hikurangi': '559', 'Tirau': '216', 'Cambridge': '213', 'Te Puke': '284', 'Hahei': '549', 'Mercer': '435', 'Porirua': '245', 'Waipu': '312', 'Te Puna': '425', 'Levin': '243', 'Whitianga - Buffalo Beach Road': '734', 'Katikati': '426', 'Rangiriri': '433', 'Cathedral Cove': '550', 'Kopu': '423', 'Bombay': '215', 'Turangi': '237', 'Tauranga - Bethlehem': '424'}

travelDateStart = date(2017,10,20)
travelDateEnd = date(2018,9,7)

filename = "MANA:%s - %s.csv" % (locationFrom.replace("/","_"), locationTo.replace("/","_"))
filenameOfInterest = "MANA:%s - %s - CHEAPAF.csv" % (locationFrom.replace("/","_"), locationTo.replace("/","_"))

startFresh = False

oneday = timedelta(1)
dayCount = 0
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

busIndex = []
busIndexNum = 0
busOfInterest = []

dateFinderURL = "https://www.manabus.com/api/search/available-dates/?originId=%s&destinationId=%s" % (locationDict[locationFrom], locationDict[locationTo])
dateFinderResponse = requests.get(dateFinderURL).json()["turnDates"]
dateDict = {}
for i in range(0,len(dateFinderResponse)):
	dateDict[str(dateFinderResponse[i]["date"])] = str(dateFinderResponse[i]["dateAsLong"])

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
			return self.price
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


while True:
	while True:
		searchDate = travelDateStart + (oneday*dayCount)
		searchDateFormated = Format(searchDate)
		try:
			dateDict[searchDateFormated]
			break
		except:
			dayCount += 1
	url = "https://www.manabus.com/api/search/do-search/?lio="+locationDict[locationFrom]+"&ldo="+locationFrom.replace(" ", "%20")+"&lid="+locationDict[locationTo]+"&ldd="+locationTo.replace(" ", "%20")+"&sdd="+dateDict[searchDateFormated]+"&srd=&srd=Return%3A+No+Return&nop=1&pc=&oneDaySearch=true&website=Mana"
	response = requests.post(url)
	busData = response.json()[0]["searchResultsTableData"]
	for i in range(0, len(busData)):
		departureTime = busData[i][1]["departureTimeDisplay"]
		arrivalTime = busData[i][1]["arrivalTimeDisplay"]

		cost = busData[i][1]["tripPrice"]
		busIndex.append(Bus(busIndexNum, searchDate, searchDate.weekday(), departureTime, arrivalTime, cost))
		busIndex[busIndexNum].describe()
		if busIndex[busIndexNum].cost() < 3:
			print "Found Cheap Bus"
			busOfInterest.append(busIndexNum)
			busIndex[busIndexNum].ofInterest()
		busIndexNum += 1
	dayCount +=1






# placeIDs = "https://www.manabus.com/api/search/travel-locations/origin/"
# response = requests.get(placeIDs)
# print response.json()[0]["name"]

# dict = {}
# for i in range(0,74):
# 	dict[str(response.json()[i]["name"])] = str(response.json()[i]["id"])
# print dict
