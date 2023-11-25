from bs4 import BeautifulSoup as bs # Import bs4 library for HTML file reader 
from urllib.request import urlopen
import json

'''
 getProductDetails(param = product_url: str) -> product details from vendors (Yody in this case, we can modify for another platform)  
 ------------------------------------------------------------------
 Function's purpose: to create Json file and fetched to LLMs models
 param: product_url to get description of product
 return : string format of description read from HTML page.
 ------------------------------------------------------------------
'''
def getProductDetails(product_url) -> str:    
    product_page = urlopen(product_url) # Product Page
    soup = bs(product_page, "html.parser") # Read product page using BeautifulSoup4
    description_element = soup.find('div', {"class": "box-promotion"}).findChildren('p', recursive=False)  # From Yody platform, get product_description
    descript = "" # Returned format 
    for p_element in description_element:
        descript = descript + p_element.get_text() + "\n"
    return descript # Description of a product

'''

'''
def createData(product_json):
    with open(product_json, 'r', encoding="utf-8") as file: 
        product_object = json.load(file)
    product_list = product_object["data"]
    for product in product_list: 
        description = getProductDetails(product["url"])
        product["details"] = description
    json_data = {
        "data": product_list
    }
    file.close()
    with open("data.json", 'w', encoding="utf-8") as output:
        json.dump(json_data, output, ensure_ascii=False, indent=4)
    return json_data

print(type(createData("productList.json")))
