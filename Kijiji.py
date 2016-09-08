from bs4 import BeautifulSoup as bs
import requests as r
import pandas as pd
import datetime
import re

headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
    }

url1 = "http://www.kijiji.ca/b-cars-trucks/oakville-halton-region/acura__audi__bmw__cadillac__ford__infiniti__lexus__mazda__mercedes+benz__mitsubishi__subaru__volkswagen__volvo-2010__/page-"
url2 = "/c174l1700277a54a68r149.0?ad=offering&price=4000__9000&kilometers=10000__80000&transmission=2&no-of-seats=4__5"

lastPage = 2
firstPage = 1

columns = ["year", "price", "mileage", "transmission", "location", "date posted", "title", "description", "url"]
df = pd.DataFrame(columns=columns)

for num in range(firstPage,lastPage + 1):
    print("processing page ", num, " of ", lastPage)
    url = url1 + str(num) + url2
    request = r.get(url, headers=headers)
    soup = bs(request.text, 'html.parser')
    for html in soup.find_all("div", "search-item"):

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


        df2 = pd.DataFrame([[str(year).lower().strip(), str(price).lower().strip(), str(mileage.replace("km", "")).lower().strip(), str(transmission).lower().strip(), str(location).lower().strip(), datePosted.lower().strip(), str(title).lower().strip(), str(description).lower().strip(), url]], columns=columns)
        df = df.append(df2)

print("done!")
df.to_csv("kijijiSearch.csv", index=False)
