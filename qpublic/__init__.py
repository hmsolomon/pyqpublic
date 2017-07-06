import requests
from bs4 import BeautifulSoup
from urllib import urlencode

class QPublic(object):
	"""docstring for QPublic"""

	def __init__(self, appName):
		super(QPublic, self).__init__()
		self.appName = appName
		self.session = requests.Session()

	def searchByOwner(self, query):
		return self.search('Name', '00', query)

	def searchByLocationAddress(self, query):
		return self.search('Address', '01', query)

	def searchByParcelNumber(self, query):
		return self.search('ParcelID', '02', query)

	def searchByRealKey(self, query):
		return self.search('AlternateID', '03', query)

	def searchByLegalInformation(self, query):
		return self.search('Name', '04', query)

	def searchByRepropKey(self, query):
		return self.search('Input', '05', query)

	def search(self, name, nbr, query):
		soup = self.get(self.searchParams())
		form = soup.form
		args = {}
		for input in form.findAll('input'):
			if input.has_attr('name'):
				args[input['name']] = ''
				value = ''
				if input.has_attr('value'):
					value = input['value']
				args[input['name']] = value

		elem = "ctlBodyPane$ctl%s$ctl01$txt%s" % (nbr, name)
		args[elem] = query
		args['__EVENTTARGET'] = 'ctlBodyPane$ctl%s$ctl01$btnSearch' % nbr
		args['__EVENTARGUMENT'] = ''

		soup = self.post(self.searchParams(), args)

		results = []
		for row in soup.table.tbody.findAll('tr'):
			tds = row.findAll('td')
			print tds[1].text
			results.append({
				'parcelId': self.normalizeText(tds[1].text),
				'alternateId': self.normalizeText(tds[2].text),
				'owner': self.normalizeText(tds[3].text),
				'propertyAddress': self.normalizeText(tds[4].text),
				'legalDescription': self.normalizeText(tds[5].text)
				})

		return results

	def buildUrl(self, params={}):
		params['App'] = self.appName
		return "https://qpublic.schneidercorp.com/Application.aspx?" + urlencode(params)

	def searchParams(self):
		return {'Layer': 'Parcels', 'PageType': 'Search'}

	def get(self, params):
		url = self.buildUrl(params)
		r = self.session.get(url)
		return self.soup(r)

	def post(self, params, data):
		url = self.buildUrl(params)
		r = self.session.post(url, data)
		return self.soup(r)

	def soup(self, req):
		return BeautifulSoup(req.text, 'html.parser')

	def normalizeText(self, text):
		return ' '.join(text.split())
