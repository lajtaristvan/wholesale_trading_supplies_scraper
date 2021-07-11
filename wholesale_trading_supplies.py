import requests
import random
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from user_agents import user_agent_list


class Wholesaletradingsupplies():

    def __init__(self, url):
        self.url = url        


    def scraper(self):
        # Pick a random uer agent
        user_agent = random.choice(user_agent_list.user_agent_list)

        # Set the headers
        headers = {
            'User-Agent': user_agent
        }

        # This is the session
        s = requests.Session() 
       
        # Make a request in a session
        r = s.get(self.url, headers=headers)

        # Scrape the content to end page
        soup = BeautifulSoup(r.content, 'lxml')

        # Scrape the end page number
        try:            
            end_page_number = int(soup.find_all('script')[8].string.strip()[21541:-785])
        except:
            end_page_number = 'no end page'

        #print(end_page_number)

        end_page = end_page_number + 1

        # A list to productlinks
        productlinks = []

        # Iterate all productlinks between a range
        for x in range(1, end_page):

            # Make a request in a session                  
            r = s.get(self.url + f'?_paged={x}', headers=headers)

            # Scrape the content
            soup = BeautifulSoup(r.content, 'lxml')

            # Identify all products
            productlist = soup.find_all('div', class_='w-full md:w-1/2 lg:w-1/3 px-8 mb-16')

            # Save all links in productlinks list
            for item in productlist:
                for link in item.find_all('a', href=True):
                    productlinks.append(link['href'])
                    #print(link['href'])

        # A list to the scraping data
        list = []

        # Iterate all links in productlinks
        for link in tqdm(productlinks):
            
            # Make requests with headers in one sessions (s)
            r = s.get(link, headers=headers)

            # Scrape the content in the soup variable with 'lxml' parser
            soup = BeautifulSoup(r.content, 'lxml')  

            # Scrape name
            try:
                name = str(soup.title.string.strip()[:-29])
            except:
                name = ''

            # Scrape barcode
            try:
                barcode = str(soup.find_all('div', class_='text-16 md:text-17 font-light flex flex-wrap mb-15')[0].find('strong', class_='font-extrabold').next_sibling.string.strip())
            except:
                barcode = ''

            # Scrape pack size
            try:
                pack_size = int(soup.find_all('p', class_='text-16 md:text-17 font-light mb-15')[0].find('strong', class_='font-extrabold').next_sibling.string.strip())
            except:
                pack_size = 1

            # Scrape netto unit price and origi price
            try:
                full_netto_unit_price_origi_price = float(soup.find('p', class_='text-18 md:text-21 font-bold text-blue-500 mr-18').text.strip()[1:-6])
                netto_unit_price_origi_price = full_netto_unit_price_origi_price / pack_size
            except:
                netto_unit_price_origi_price = ''

            # Define the gross unit price and origi price
            gross_unit_price_origi_price = float(netto_unit_price_origi_price * 1.2)

            # VAT calculation
            vat = round(((gross_unit_price_origi_price - netto_unit_price_origi_price) / netto_unit_price_origi_price) * 100)            

            # Scrape availability         
            availability = True

            # Define a dictionary for csv
            wholesaletradingsupplies = {                 
                'link': link,
                'name': name,
                'barcode': barcode,
                'pack_size': pack_size,
                'netto_unit_price_origi_price': netto_unit_price_origi_price,
                'gross_unit_price_origi_price': gross_unit_price_origi_price,
                'vat': vat,                       
                'availability': availability
            }

            # Add the dictionary to the list every iteration
            list.append(wholesaletradingsupplies)

            # Print every iteration        
            # print(
            #     '\n--------- Saving: ---------\n'             
            #     'link: ' + str(wholesaletradingsupplies['link']) + '\n'
            #     'name: ' + str(wholesaletradingsupplies['name']) + '\n'
            #     'barcode: ' + str(wholesaletradingsupplies['barcode']) + '\n'
            #     'pack size: ' + str(wholesaletradingsupplies['pack_size']) + '\n'
            #     'netto unit price origi price: ' + str(wholesaletradingsupplies['netto_unit_price_origi_price']) + '\n'
            #     'gross unit price origi price: ' + str(wholesaletradingsupplies['gross_unit_price_origi_price']) + '\n'
            #     'vat: ' + str(wholesaletradingsupplies['vat']) + '\n'            
            #     'availability: ' + str(wholesaletradingsupplies['availability']) + '\n'
            # )

        # Make table to list
        df = pd.DataFrame(list)

        # Save to csv       
        df.to_csv(r'C:\WEBDEV\wholesale_trading_supplies_scraper\exports\wholesaletradingsupplies.csv', mode='a', index=False, header=True)


get_wholesaletradingsupplies_all = Wholesaletradingsupplies('https://wholesaletradingsupplies.com/shop/')

get_wholesaletradingsupplies_all.scraper()
