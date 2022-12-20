# import module
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from credentials import *
import pandas as pd
from azure.storage.blob import BlockBlobService
import io


HEADERS = ({'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


# user define function
# Scrape the data
def getdata(url):
    r = requests.get(url, headers=HEADERS)
    return r.text


def html_code(url):
    # pass the url
    # into getdata function
    htmldata = getdata(url)
    soup = BeautifulSoup(htmldata, 'html.parser')

    # display html code
    return (soup)


url = review_url

soup = html_code(url)
#print(soup)

def cus_data(soup):
	# find the Html tag
	# with find()
	# and convert into string
	data_str = ""
	cus_list = []

	for item in soup.find_all("span", class_="a-profile-name"):
		data_str = data_str + item.get_text()
		cus_list.append(data_str)
		data_str = ""
	return cus_list


cus_res = cus_data(soup)
#print(cus_res)

def cus_rev(soup):
	# find the Html tag
	# with find()
	# and convert into string
	data_str = ""

	for item in soup.find_all("span", class_="a-size-base cr-lightbox-review-body"):
		data_str = data_str + item.get_text()

	result = data_str.split("\n")
	return (result)


rev_data = cus_rev(soup)
rev_result = []
for i in rev_data:
	if len(i) ==0:
		pass
	else:
		rev_result.append(i)

print("rev data is ",rev_result)

#--------------------------------------------------------------------------------
subscription_key = cognitive_service_subscription_key
endpoint = cognitive_service_endpoint

sentiment_url = endpoint + "/text/analytics/v3.0/sentiment"

data_list =[]
count =0
for i in rev_data:
	if count == 10:
		break
	elif len(i.strip()) == 0:
		pass
	else:
		samp_dict = {"id": str(count), "language": "en", "text": str(i)}
		data_list.append(samp_dict)
		count += 1

print(data_list)

documents = {"documents": data_list}
print(documents)
headers = {"Ocp-Apim-Subscription-Key": subscription_key}
print(headers)
response = requests.post(sentiment_url, headers=headers, json=documents)
sentiments = response.json()
pprint(sentiments['documents'])

final_review_data = {}
for i in range(10):
	try:
		final_review_data[i+1] = sentiments['documents'][i]['sentiment']
	except Exception as e:
		break

print(final_review_data)

df_data = pd.DataFrame.from_dict(final_review_data,orient = 'index',columns = ['sentiment'])
print("final data frame is \n",df_data)

output = io.StringIO()
output = df_data.to_csv(index_label="idx",encoding = "utf-8")
print("output is ",output)

blobService = BlockBlobService(account_name=accountName,account_key=accountKey)
blobService.create_blob_from_text(containerName,'SentimentsOutData.csv',output)
