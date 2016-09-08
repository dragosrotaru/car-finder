from bs4 import BeautifulSoup as bs
import requests as r
import pandas as pd
import re

headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
    }

url = "http://wwwa.autotrader.ca/cars/on/oakville/?prx=100&prv=Ontario&loc=L6H3V2&trans=Automatic&body=Sedan&sts=New-Used&pRng=4000%2c9000&oRng=10000%2c80000&yRng=2010%2c&hprc=True&wcp=True&inMarket=advancedSearch&rcs=0&rcp=10000"

columns = ["year", "price", "mileage", "distance", "title", "description", "url"]
df = pd.DataFrame(columns=columns)

print("retrieving...")
request = r.get(url, headers=headers)
print("retrieved")
soup = bs(request.text, 'html.parser')
count = 1
for html in soup.find_all("div", "resultItem"):
    print( "retrieving result ", count)
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
    mileage = tag.text.replace(" km", "")

    tag = html.find("div", "ResultDistance")
    distance = tag.contents[0]


    df2 = pd.DataFrame([[str(year).lower().strip(), str(price).lower().strip(), str(mileage).lower().strip(), str(distance).lower().strip(), str(title).lower().strip(), str(description).lower().strip(), url]], columns=columns)
    df = df.append(df2)

print("done!")
df.to_csv("AutoTraderSearch.csv", index=False)
