import json
import sys, getopt
import urllib.request
from pprint import pprint
from datetime import datetime


def CallUrl(url):
    response = urllib.request.urlopen(url).read()
    jsonData = json.loads(response)
    return jsonData


def ConvertStringToDateTime(dateStr):
    datetime_str = datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S")
    datetime_object = datetime_str.strftime("%d-%B-%y %H:%M:%S")
    return datetime_object


def main(inputAirport, startDate, endDate, maxReturnPrice):
    urlToGetAllRoutes = "https://api.ryanair.com/aggregate/4/common?embedded=airports"
    allAirports = CallUrl(urlToGetAllRoutes)
    availableRoutes = []

    for eachAirport in allAirports["airports"]:
        if eachAirport["iataCode"] == inputAirport:
            for eachRoute in eachAirport["routes"]:
                if "airport" in eachRoute:
                    availableRoutes.append(eachRoute)
    availableRoutes = [s.replace("airport:", "") for s in availableRoutes]

    availableRoutesWithInputDates = []
    for eachAirport in availableRoutes:
        urlToGetAllAvailabilities = (
            "https://services-api.ryanair.com/farfnd/3/oneWayFares/%s/%s/availabilities"
        ) % (inputAirport, eachAirport)
        allAvailabilities = CallUrl(urlToGetAllAvailabilities)
        if startDate in allAvailabilities and endDate in allAvailabilities:
            availableRoutesWithInputDates.append(eachAirport)

    allAvailableFlights = []
    index = 1
    for eachAvailableRoute in availableRoutesWithInputDates:
        urlToGetFlightData = (
            "https://services-api.ryanair.com/farfnd/3/roundTripFares?&arrivalAirportIataCode=%s&departureAirportIataCode=%s&"
            "inboundDepartureDateFrom=%s&inboundDepartureDateTo=%s&limit=16&offset=0&outboundDepartureDateFrom=%s&"
            "outboundDepartureDateTo=%s&priceValueTo=%s"
        ) % (
            eachAvailableRoute,
            inputAirport,
            endDate,
            endDate,
            startDate,
            startDate,
            maxReturnPrice,
        )
        allFlights = CallUrl(urlToGetFlightData)
        if allFlights["total"] != 0:
            outBoundObject = {
                "departureDateTime": ConvertStringToDateTime(
                    allFlights["fares"][0]["outbound"]["departureDate"]
                ),
                "arrivalDateTime": ConvertStringToDateTime(
                    allFlights["fares"][0]["outbound"]["arrivalDate"]
                ),
                "price": allFlights["fares"][0]["outbound"]["price"]["value"],
            }
            inBoundObject = {
                "departureDateTime": ConvertStringToDateTime(
                    allFlights["fares"][0]["inbound"]["departureDate"]
                ),
                "arrivalDateTime": ConvertStringToDateTime(
                    allFlights["fares"][0]["inbound"]["arrivalDate"]
                ),
                "price": allFlights["fares"][0]["inbound"]["price"]["value"],
            }
            flightInfoObject = {
                "origin": allFlights["fares"][0]["outbound"]["departureAirport"][
                    "name"
                ],
                "destination": allFlights["fares"][0]["outbound"]["arrivalAirport"][
                    "name"
                ],
                "outbound": outBoundObject,
                "inbound": inBoundObject,
                "totalPrice": round(
                    allFlights["fares"][0]["outbound"]["price"]["value"]
                    + allFlights["fares"][0]["inbound"]["price"]["value"],
                    2,
                ),
            }
            newJsonObject = {"num": index, "flightInfo": flightInfoObject}
            index += 1
            allAvailableFlights.append(newJsonObject)

    # print(allAvailableFlights)

    newJsonFlightsObject = {"allFlights": allAvailableFlights}
    print(json.dumps(newJsonFlightsObject))

if __name__ == "__main__":
    inputAirport = str(sys.argv[1])
    startDate = str(sys.argv[2])
    endDate = str(sys.argv[3])
    maxReturnPrice = int(sys.argv[4])
    
    main(inputAirport, startDate, endDate, maxReturnPrice)

# Call with example: python holidayPicker.py "CRL" "2019-08-14" "2019-08-20" 150 > data.json
