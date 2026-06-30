import os
from bs4 import BeautifulSoup

file = os.listdir('data')
print(file)


with open(f'data/{file[0]}','r') as f:
    html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    title_row = soup.find('p',class_ = 'ds-text-tight-s').get_text()
    # title = title_row[0]+" " +title_row[1]+" "+title_row[2]
    print(title_row)
    stat_header = soup.find_all('th',class_ = 'ds-bg-fill-content-alternate')
    required_header_list = []
    for i in range(0,len(stat_header)):
        text = stat_header[i].get_text(strip=True)
        required_header_list.append(text)
    value = required_header_list.index('Tournament')
    print(required_header_list)
    print(value)
    
    
    # data_rows = soup.find_all('tr',class_='ds-bg-fill-canvas')
    # for row in data_rows:
    #     data = row.find_all('td')
    #     # print(data)
    #     # print(len(data))
    #     for i in range(0,len(data)):
    #         tournament = data[0].find('span').get_text(strip=True)
    #         if not tournament.startswith('IPL '):
    #             continue
    #         else:
    #             print(data[i].find('span').get_text(strip=True))