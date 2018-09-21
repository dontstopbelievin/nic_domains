from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import urllib.request
import mysql.connector

my_url = 'https://nic.kz/'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent}
request=urllib.request.Request(my_url,None,headers)

uClient = uReq(request)
page_html = uClient.read()
uClient.close()

page_soup = soup(page_html, "html.parser")

containers = page_soup.findAll("table", {"id":"last-ten-table"})
table = containers[0].findAll("table",{})
rows = table[0].findAll("tr",{})

#Manually create database nic and table domains to make this code work
con = mysql.connector.connect(user="root",password="",host="localhost",database="nic")
db = con.cursor(buffered=True)

links = [0] * 10
index = 0

for row in rows:

	cols = row.findAll("td",{})
	links[index] = 'https://nic.kz' + cols[1].a["href"]
	index += 1

i = 0
values = [0] * 180

while i < len(links):
	my_url = links[i]
	request=urllib.request.Request(my_url,None,headers)
	uClient = uReq(request)
	page_html = uClient.read()
	uClient.close()
	page_soup = soup(page_html, "html.parser")
	containers = page_soup.findAll("pre", {})
	results = containers[0].text.splitlines()
	for j in range(18):
		row = results[j].split(':')
		if(len(row) >= 2):
			values[i*18+j] = row[1].strip()
		j += 1

	i += 1

i = 0
while i < 10:
	insert_stmt = ("""select id from nic.domains where domain_name = %(domain)s""")
	db.execute(insert_stmt, { 'domain': values[i*18] })
	if db.rowcount == 0:
		insert_stmt = ("""insert into nic.domains (domain_name, name, organization_name, street_address, city, state, postal_code, country, nic_handle,
		agent_name, phone_number, fax_number, email) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
		data = (values[i*18+0], values[i*18+3], values[i*18+4], values[i*18+5], values[i*18+6], values[i*18+7], values[i*18+8], values[i*18+9], values[i*18+12], values[i*18+13], values[i*18+14], values[i*18+15], values[i*18+16])
		db.execute(insert_stmt, data)
	i += 1
con.commit()