from bs4 import BeautifulSoup as bs
import requests as r
import pandas as pd
import datetime
import re


#User agent changed to avoid connection "problems"
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
    }

#put your urls here:
#Kijiji: make sure url includes "page-1" in query string
#AutoTRADER: make sure "rcp=" is included in the query string and the value is larger then result number
AUTOTRADER_URL = "http://wwwa.autotrader.ca/cars/on/oakville/?prx=25&prv=Ontario&loc=L6H3V2&trans=Automatic&sts=New-Used&pRng=4000%2c8000&oRng=20000%2c100000&yRng=2010%2c2014&hprc=True&wcp=True&inMarket=advancedSearch&rcs=0&rcp=100"
KIJIJI_URL= "http://www.kijiji.ca/b-cars-trucks/oakville-halton-region/2010__2015/page-1/c174l1700277a68r25.0?ad=offering&price=4000__8000&kilometers=20000__100000&transmission=2"

#page numbers for Kijiji Results
lastPage = 2
firstPage = 1

columns = ["source", "date posted", "title", "description", "url", "transmission", "location", "price", "year", "mileage"]


def retrieveKijiji(df):
    print("retrieving Kijiji...")
    count = 1
    for num in range(firstPage,lastPage + 1):
        url = KIJIJI_URL.replace("page-1", "page-" + str(num))
        request = r.get(url, headers=HEADERS)
        soup = bs(request.text, 'html.parser')
        for html in soup.find_all("div", "search-item"):
            print( "retrieving result ", count, end="\r")
            count = count + 1
            tag = html.find("a", "title")
            title = tag.text
            year = tag.contents[0].split()[0]
            if not re.match(r"^[12][0-9]{3}$" , year):
                year = None
            url = "http://www.kijiji.ca" + str(tag['href'])

            tag = html.find("div", "description")
            if (tag.find("div", "details") and not tag.find("span", "car-proof")):
                description = tag.contents[0]
                tag = tag.find("div", "details")
                tokenized_description = tag.contents[0].split()
                try:
                    mileage = tokenized_description[-3]
                    transmission = tokenized_description[-1]
                except Exception as e:
                    mileage = tokenized_description[-1]
                    transmission = None
            elif tag.find("div", "details") and tag.find("span", "car-proof"):
                description = tag.contents[0]
                tag = tag.find("div", "details")
                tokenized_description = tag.contents[0].split()
                mileage = tokenized_description[0]
                transmission = tokenized_description[2]
            else:
                tokenized_description = tag.text.split()
                d = ' '
                description = d.join(tokenized_description[:-3])
                mileage = tokenized_description[-3]
                transmission = tokenized_description[-1]

            tag = html.find("span", "date-posted")
            if (tag.text[0] == "<"):
                datePosted = datetime.datetime.today().strftime("%d/%m/%Y")
            elif (tag.text[0] == 'Y'):
                datePosted = (datetime.datetime.today()- datetime.timedelta(days=1)).strftime("%d/%m/%Y")
            else:
                datePosted = tag.text

            tag = html.find("div", "price")
            price = tag.text

            tag = html.find("div", "location")
            location = tag.contents[0]

            df2 = pd.DataFrame([["Kijiji", datePosted, str(title).lower().strip(), str(description).lower().strip(), url, str(transmission).lower().strip(), str(location).lower().strip(), str(price).lower().strip(), str(year).lower().strip(), str(mileage).replace('km', '').lower().strip()]], columns=columns)
            df = df.append(df2)
    return df

def retrieveAutoTRADER(df):
    print("\nretrieving autoTRADER...")
    request = r.get(AUTOTRADER_URL, headers=HEADERS)
    soup = bs(request.text, 'html.parser')
    count = 1
    for html in soup.find_all("div", "resultItem"):
        try:
            print( "retrieving result ", count, end="\r")
            count = count + 1
            tag = html.find("span", "resultTitle")
            title = tag.text
            year = tag.contents[0].split()[0]
            if not re.match(r"^[12][0-9]{3}$" , year):
                year = None

            tag = html.find("h2").find("a")
            url = str(tag['href'])

            tag = html.find("p", "at_details")
            description = tag.text

            tag = html.find("div", "at_price")
            price = tag.contents[-1]

            tag = html.find("div", "at_km")
            mileage = tag.text

            tag = html.find("div", "ResultDistance")
            location = tag.contents[0]

            df2 = pd.DataFrame([["autoTRADER", None, title.lower().strip(), description.lower().strip(), url, None, location.lower().strip(), price.lower().strip(), year.lower().strip(), mileage.replace('km', '').lower().strip()]], columns=columns)
            df = df.append(df2)
        except Exception as e:
            print("result error")
    return df

def main():
    df = pd.DataFrame(columns=columns)
    df = retrieveKijiji(df)
    df = retrieveAutoTRADER(df)
    numberResults = len(df.index)
    print("\ndone! " + str(numberResults) + " results found")
    df = df.drop_duplicates(["title", "year", "mileage", "price"])
    df['YearScore'] = '=([@year] - MIN([year])) / (MAX([year]) - MIN([year]))'
    df['MileageScore'] = '=(MAX([mileage]) - [@mileage]) / (MAX([mileage]) - MIN([mileage]))'
    df['PriceScore'] = '=(MAX([price]) - [@price]) / (MAX([price]) - MIN([price]))'
    df['TotalScore'] = '=[@MileageScore]+[@YearScore]+[@PriceScore]'
    df['PMScore'] = '=[@MileageScore]+[@PriceScore]'
    df.to_csv(datetime.datetime.today().strftime("%Y-%m-%d") + "-CarSearchOutput.csv", index=False)
    print("file saved")
if __name__ == '__main__':
    main()
