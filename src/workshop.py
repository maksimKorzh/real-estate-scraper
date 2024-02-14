####################################################
#
#  Example real estate properties scraper workshop
#
####################################################

import datetime, json, requests
from scrapy.selector import Selector

name = 'otodom'
start_page = 1
base_url = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska?page=1&limit=36&daysSinceCreated=1&by=PRICE&direction=ASC&viewType=listing'
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
custom_settings = {'CONCURRENT_REQUESTS_PER_DOMAIN': 2, 'DOWNLOAD_DELAY': 1}
filename = './output/Residential_' +('Rent' if 'wynajem' in base_url else 'Sale') + '_Flats_' + datetime.datetime.today().strftime('%Y-%m-%d-%H-%M') + '.csv'
columns = [
  'id', 'advertiserType', 'advertType', 'createdAt', 'modifiedAt', 'description', 'features', 'characteristics',
  'latitude', 'longitude', 'street_name', 'street_number', 'subdistrict', 'district', 'city', 'county', 'province', 
  'postalCode', 'map_url', 'title'
]

def get_links(response):
  data = json.loads(response.css('script[id="__NEXT_DATA__"]::text').get())['props']['pageProps']['data']['searchAds']['items']
  return ['https://www.otodom.pl/pl/oferta/' + link['slug'] for link in data]

def get_total_pages(response):
  try: return json.loads(response.css('script[id="__NEXT_DATA__"]::text').get())['props']['pageProps']['tracking']['listing']['page_count']
  except: return 1

def get_next_page(url, current_page):
  split_url = url.split('?')
  if len(split_url) == 2:
    params = '&' + '&'.join([i for i in split_url[1].split('&') if 'page' not in i])
  else: params = ''
  return split_url[0] + '?page=' + str(current_page) + params

def extract_features(response, verbose):
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
  if verbose: print(json.dumps(extract_features, indent=2))
  return extract_features

def save_response(url, filename):
  response = requests.get(url, headers=headers)
  with open(filename, 'w') as f: f.write(response.text)
  print('Download complete')

def load_response(filename):
  with open(filename) as f: response = Selector(text=f.read())
  return response

def test_links(cache, url):
  if not cache: save_response(url, 'links.html')
  response = load_response('links.html')
  print('Links:', get_links(response))
  print('Total pages:', get_total_pages(response))
  print('Next page:', get_next_page(url, 3))

def test_listing(cache, url):
  if not cache: save_response(url, 'listing.html')
  response = load_response('listing.html')
  print('Features: ', extract_features(response, True))

if __name__ == '__main__':
  cache = True
  try:
    test_links(cache, 'https://www.otodom.pl/pl/wyniki/sprzedaz/lokal/cala-polska')
    test_listing(cache, 'https://www.otodom.pl/pl/oferta/mieszkanie-lokal-3-pokoje-65m2-pilotow-olsza-ID4p8LL')
  except: print('Set cache = False')
