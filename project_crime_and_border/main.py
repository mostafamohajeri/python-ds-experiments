import csv
import urllib.request
import os
from math import *
from bs4 import BeautifulSoup
import re
import scipy

san_ysidro = [32.5556, -117.0470]
yuma = [32.6927, -114.6277]
tuscon = [32.2226, -110.9747]
elpaso = [31.7619, -106.4850]
laredo = [27.5036, -99.5076]
del_rio = [29.3709, -100.8959]
brown = [25.9017, -97.4975]

border = [san_ysidro, yuma, tuscon, elpaso, laredo, del_rio, brown]


def getDocument(url):
    parts = url.split("/")

    file_name = "data/" + parts[len(parts) - 1]
    createDataDirectory("data")

    if os.path.isfile(file_name):
        print("File exist, reading from file")

        with open(file_name, 'r') as content_file:
            content = content_file.read()
            return content
    else:
        response = urllib.request.urlopen(url)
        data = response.read()
        content = data.decode('utf-8')
        f = open(file_name, 'wb')
        f.write(data)
        return content
    pass


def parseTable(htmlFile):
    # returns 2d list of table in html file
    data = list()
    main_page = getDocument(htmlFile)
    soup = BeautifulSoup(main_page, features="html.parser")
    table = soup.find("table")
    rows = list()
    for row in table.findAll("tr"):
        if "href" in str(row):
            try:
                city_name = row.findAll("td")[1].find("a").contents[0]
                city_href = 'https://en.wikipedia.org/' + row.findAll("td")[1].find("a")['href']
                crime_rate_column = row.findAll("td")[3].contents[0]
                rows.append([city_name, city_href, crime_rate_column])

            except:  # Some cities do not have any data, so we just pass
                pass

    return rows


def getCoordinates(url):
    page = getDocument(url)
    soup = BeautifulSoup(page, features="html.parser")
    lat = soup.find("span", {"class": "latitude"}).contents[0]
    lon = soup.find("span", {"class": "longitude"}).contents[0]

    return dms_to_dd(str(lat), str(lon))


def findDistance(coordinate1, coordinate2):
    # returns distance between two coordinates
    lat_1,lon_1 = map(radians,coordinate1)
    lat_2,lon_2 = map(radians, coordinate2)

    epsilon = acos(sin(lon_1) * sin(lon_2) + cos(lon_1) * cos(lon_2) * cos(fabs(lat_1 - lat_2)))

    return (3958.756 * epsilon)



def createResultTable(table):

    file_path = "data/results.csv"

    out = list()

    for row in table:
        dd_lat_lon = row[1]
        smallest_distance = 9999999999
        for border_city in border:

            distance = findDistance(dd_lat_lon, border_city)
            if distance < smallest_distance:
                smallest_distance = distance
            print(row[0], smallest_distance,distance)

        out.append([row[0], row[2], smallest_distance])

    with open(file_path, "w+") as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(out)

    return out


def printCorrelation(file):
    file_path = file

    if os.path.exists(file_path):
        print("csv file already there")
        with open(file_path, newline='') as csvfile:
            data = list(csv.reader(csvfile))
            print(data)

        crime_rates = []
        distances = []

        for item in data:
            crime_rates.append(float(item[1]))
            distances.append(float(item[2]))

        print(scipy.corrcoef(crime_rates, distances))

    else: print("No csv file was found!")


def createDataDirectory(path):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        print(path, "was already there")


def dms_to_dd(lat, lon):
    N = 'N' in lat
    dms = re.split('°|′|″', lat[:-2])
    d = float(dms[0])
    m = float(dms[1])
    s = 0 if len(dms) < 3 else float(dms[2])
    latitude = (d + m / 60. + s / 3600.) * (1 if N else -1)

    W = 'W' in lon
    dms = re.split('°|′|″', lon[:-2])
    d = float(dms[0])
    m = float(dms[1])
    s = 0 if len(dms) < 3 else float(dms[2])
    longitude = (d + m / 60. + s / 3600.) * (-1 if W else 1)

    return [latitude, longitude]



def getAllCoordinates():
    table = parseTable("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_crime_rate")

    for row in table:
        dd_lat_lon = getCoordinates(row[1])
        row[1] = dd_lat_lon

    return table


def main():

    table = getAllCoordinates()
    createResultTable(table)
    printCorrelation(file = "data/results.csv")

    pass


if __name__ == "__main__":
    main()
