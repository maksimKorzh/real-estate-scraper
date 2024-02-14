##########################################################
#
#  General purpose real estate properties data collector
#
##########################################################

import sys,  csv, json, scrapy, datetime, workshop
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector

class Otodom(scrapy.Spider):
    name = workshop.name
    base_url = workshop.base_url 
    headers = workshop.headers
    custom_settings = workshop.custom_settings
    
    def start_requests(self):
      filename = workshop.filename
      columns = workshop.columns
      with open(filename, 'w') as f: f.write(','.join(columns) + '\n')
      yield scrapy.Request(
          url=self.base_url,
          headers=self.headers,
          meta={
            'filename': filename,
            'current_page': workshop.start_page
          }, callback=self.parse_links
      )

    def parse_links(self, response):
      filename = response.meta.get('filename')
      current_page = response.meta.get('current_page')
      # get_links()
      for card_url in workshop.get_links(response):
        yield response.follow(
          url=card_url,
          headers=self.headers,
          meta={'filename': filename},
          callback=self.parse_listing
        )
      try:
        # get_total_pages()
        total_pages = workshop.get_total_pages(response)
        current_page += 1
        if current_page <= total_pages:
          next_page = workshop.get_next_page(response.url, current_page)
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
        features = workshop.extract_features(response, False)
        with open(filename, 'a', encoding='utf-8') as csv_file:
          writer = csv.DictWriter(csv_file, features.keys())
          writer.writerow(features)
      except: pass

if __name__ == '__main__':
  process = CrawlerProcess()
  process.crawl(Otodom)
  process.start()
