#########################################
#
#  Generate production web scraper code
#
#########################################

import scrape, workshop, inspect

src = inspect.getsource(scrape)
get_links = inspect.getsource(workshop.get_links)
get_links_lines = get_links.split('\n')
get_links = get_links_lines[1].replace('  ', '') + '\n' + get_links_lines[2].replace('  ', ' '*6)
get_links = get_links.replace('return', 'links =')
get_total_pages = inspect.getsource(workshop.get_total_pages)
get_total_pages_lines = get_total_pages.split('\n')
get_total_pages = get_total_pages_lines[1].replace('  ', '') + '\n' + get_total_pages_lines[2].replace('  ', ' '*8)
get_total_pages = get_total_pages.replace('return', 'total_pages =')
extract_features = inspect.getsource(workshop.extract_features)
extract_features_lines = [' '*6 + line for line in extract_features.split('\n')]
extract_features = '\n'.join(extract_features_lines[1:-3])
get_next_page = inspect.getsource(workshop.get_next_page)
get_next_page_lines = [' '*8 + line for line in get_next_page.split('\n')]
get_next_page = '\n'.join(get_next_page_lines[1:])
get_next_page = get_next_page.replace('return', 'next_page =')
get_next_page = get_next_page.replace('url.split', 'response.url.split')
src = src.replace('scrape', '')
src = src.replace('collector', 'web scraper')
src = src.replace(', workshop', '')
src = src.replace('General purpose', '   ' + workshop.name.capitalize())
src = src.replace('workshop.name', "'" + workshop.name + "'")
src = src.replace('workshop.filename', "'" + workshop.filename + "'")
src = src.replace('workshop.start_page', str(workshop.start_page))
src = src.replace('workshop.base_url', "'" + workshop.base_url + "'")
src = src.replace('workshop.headers', str(workshop.headers))
src = src.replace('workshop.custom_settings', str(workshop.custom_settings))
src = src.replace('workshop.columns', str(workshop.columns))
src = src.replace('# get_links()', get_links)
src = src.replace('# get_total_pages()', get_total_pages)
src = src.replace('workshop.get_links(response)', 'links')
src = src.replace('total_pages = workshop.get_total_pages(response)', '')
src = src.replace('        features = workshop.extract_features(response, False)', extract_features)
src = src.replace('          next_page = workshop.get_next_page(response.url, current_page)', get_next_page)
print('Web scraper source code has been generated')
with open(workshop.name + '.py', 'w') as f: f.write(src)
