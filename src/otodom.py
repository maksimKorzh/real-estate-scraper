##########################################################
#
#     Otodom real estate properties data web scraper
#
##########################################################

import sys,  csv, json, scrapy, datetime
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class Otodom(scrapy.Spider):
    name = 'otodom'
    base_url = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska?page=1&limit=36&daysSinceCreated=1&by=PRICE&direction=ASC&viewType=listing' 
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    custom_settings = {'CONCURRENT_REQUESTS_PER_DOMAIN': 2, 'DOWNLOAD_DELAY': 1}
    
    def start_requests(self):
      filename = './output/Residential_Rent_Flats_2024-02-13-18-23.csv'
      columns = ['id', 'advertiserType', 'advertType', 'createdAt', 'modifiedAt', 'description', 'features', 'characteristics', 'latitude', 'longitude', 'street_name', 'street_number', 'subdistrict', 'district', 'city', 'county', 'province', 'postalCode', 'map_url', 'title']
      with open(filename, 'w') as f: f.write(','.join(columns) + '\n')
      yield scrapy.Request(
          url=self.base_url,
          headers=self.headers,
          meta={
            'filename': filename,
            'current_page': 1
          }, callback=self.parse_links
      )

    def parse_links(self, response):
      filename = response.meta.get('filename')
      current_page = response.meta.get('current_page')
      data = json.loads(response.css('script[id="__NEXT_DATA__"]::text').get())['props']['pageProps']['data']['searchAds']['items']
      links = ['https://www.otodom.pl/pl/oferta/' + link['slug'] for link in data]
      for card_url in links:
        yield response.follow(
          url=card_url,
          headers=self.headers,
          meta={'filename': filename},
          callback=self.parse_listing
        )
      try:
        try: total_pages = json.loads(response.css('script[id="__NEXT_DATA__"]::text').get())['props']['pageProps']['tracking']['listing']['page_count']
        except: total_pages = 1
        
        current_page += 1
        if current_page <= total_pages:
          split_url = response.url.split('?')
          if len(split_url) == 2:
            params = '&' + '&'.join([i for i in split_url[1].split('&') if 'page' not in i])
          else: params = ''
          next_page = split_url[0] + '?page=' + str(current_page) + params
        
          print('PAGE %s | %s' % (current_page, total_pages), next_page)
          yield response.follow(
            url=next_page,
            headers=self.headers,
            meta={'filename': filename, 'current_page': current_page},
            callback=self.parse_links
          )
      except Exception as e: print(e)
        
    def parse_listing(self, response):
      filename = response.meta.get('filename')
      try:
        features = json.loads(response.css('script[id="__NEXT_DATA__"]::text').get())['props']['pageProps']['ad']
        extract_features = {
          'id': features['id'],
          'advertiserType': features['advertiserType'],
          'advertType': features['advertType'],
          'createdAt': features['createdAt'],
          'modifiedAt': features['modifiedAt'],
          'description': features['description'].strip().replace('\r\n', '').replace('\n', ''),
          'features': features['features'],
          'characteristics': []         
        }
        for item in features['characteristics']:
          extract_features['characteristics'].append({item['key']: item['value']})
        extract_features.update({'latitude': features['location']['coordinates']['latitude']})
        extract_features.update({'longitude': features['location']['coordinates']['longitude']})
        try: extract_features.update({'street_name': features['location']['address']['street']['name']})
        except: extract_features.update({'street_name': features['location']['address']['street']})
        try: extract_features.update({'street_number': features['location']['address']['street']['number']})
        except: extract_features.update({'street_number': features['location']['address']['street']})
        extract_features.update({'subdistrict': features['location']['address']['subdistrict']})
        extract_features.update({'district': features['location']['address']['district']})
        extract_features.update({'city': features['location']['address']['city']['name']})
        extract_features.update({'county': features['location']['address']['county']['code']})
        extract_features.update({'province': features['location']['address']['province']['code']})
        extract_features.update({'postalCode': features['location']['address']['postalCode']})
        extract_features.update({'map_url': features['url'] + '#map'})
        extract_features.update({'title': features['title']})
        with open(filename, 'a', encoding='utf-8') as csv_file:
          writer = csv.DictWriter(csv_file, features.keys())
          writer.writerow(features)
      except: pass

if __name__ == '__main__':
  process = CrawlerProcess()
  process.crawl(Otodom)
  process.start()
