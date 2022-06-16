import requests, pickle, sys, glob2, re, pprint, operator

from bs4 import BeautifulSoup

def load_file(filename):
	file = open(filename, 'rb');
	dict = pickle.load(file);
	file.close();
	return dict;

def save_file(filename, web_dict):
	file = open(filename, 'wb+');
	pickle.dump(web_dict, file);
	file.close();

#get covered packages
def get_packages(file_name):
	packages = {}
	for file in glob2.iglob(file_name, recursive=True):
		with open(file, "r") as coverage_html_file:
			soup = BeautifulSoup(coverage_html_file, 'html.parser')
		table = soup.find('table')
		body = table.find('tbody')
		for tr in body.find_all('tr'):
			ttr = tr.find('td')
			a = ttr.find('a')
			packageName = (a.text).strip()
			td =  tr.find_all('td', {'class':"ctr2"})
			if (td[0].text).strip() != '0%':
				packages[packageName] = " "
	return packages;

#get covered classes
def get_classes(file_name):
	classes = {}
	for file in glob2.iglob(file_name, recursive=True):
		with open(file, "r") as coverage_html_file:
			soup = BeautifulSoup(coverage_html_file, 'html.parser')
		table = soup.find('table')
		body = table.find('tbody')
		for tr in body.find_all('tr'):
			ttr = tr.find('td')
			a = ttr.find('a')
			class_Name = (a.text).strip()
			class_file_name = a['href']
			td =  tr.find_all('td', {'class':"ctr2"})
			if (td[0].text).strip() != '0%':
				classes[class_Name] = class_file_name
	return classes;
#get covered methods
def get_methods(file_name):
	meth_file = file_name + ".html"
	methods = []
	for file in glob2.iglob(meth_file, recursive=True):
		with open(file, "r") as coverage_html_file:
			soup = BeautifulSoup(coverage_html_file, 'html.parser')
		table = soup.find('table')
		body = table.find('tbody')
		for tr in body.find_all('tr'):
			ttr = tr.find('td')
			a = ttr.find('a')
			line_number = ""
			if a is not None and 'href' in a.attrs:
				line_number = a.attrs['href']
				line_number = line_number.split("L")[-1]
				#print("line Number: ", line_number )
				method = (ttr.text).strip()
				td =  tr.find_all('td', {'class':"ctr2"})
				if (td[0].text).strip() != '0%':
					method = re.sub(r'\(.*?\)', '', method)
					if(method != 'static {...}' and method != '{...}'):
						ms = method.split(".");
						if(len(ms) > 1):
							method = ms[len(ms) - 1]
					#print("method: ", method, "line#: ", line_number)
						if line_number != "" and method is not None:
							methods.append(tuple((method, int(line_number))))
	methods.sort(key = operator.itemgetter(1))
	#print("method: ", methods)
	return methods
def get_statements(file_name, methods):
	statements = {}
	for (i,j) in methods:
		statements[i] = []
	statemet_line = ""
	for file in glob2.iglob(file_name, recursive=True):
		with open(file, "r", encoding='utf8') as coverage_html_file:
			soup = BeautifulSoup(coverage_html_file, 'html.parser')
			body = soup.find('body')
			class_code = body.find('pre', {'class': "source lang-java linenums"})
			source_code = class_code.find('ol', {'class': "linenums"})
			for span in class_code.find_all('span', {"class": lambda class_: class_ in ("fc", "pc bpc")}):
				statemet_line = span['id']
				statemet_line = statemet_line.split("L")[-1]
				line_number = int(statemet_line)
				statement = span.text
				statement = statement.strip()
				if len(methods) != 0 :
					if len(methods) != 1 :
						curent = methods[0][1]
						next = methods[1][1]
						if line_number < methods[0][1]:
							pass
						elif line_number >= methods[0][1] and line_number < methods[1][1]:
							statements[methods[0][0]].append(statement)
						else:
							statements[methods[1][0]].append(statement)
							methods.remove((methods[0][0], methods[0][1]))
					else:
						if line_number >= methods[0][1]:
							method = methods[0][0]
							statements[method].append(statement)
	return statements;
if __name__ == "__main__":

	Covered_classes = {}
	coverage = {}
	statements = {}

	#for file in glob.iglob("/home/jihan/Downloads/jacoco/[a-z]/*.html", recursive=True):
	#for file in glob.iglob("/home/jihan/Downloads/testingCoverage/**/Test?/index.html", recursive=True):
	base_file_name = sys.argv[2];
	html_file = "index.html"
	file_name = base_file_name + html_file

	packages = get_packages(file_name)
	for package in packages.keys():
		#print("package: ", package)
		#temp_file_name = base_file_name + str(package) + "/"
		#file_name = temp_file_name + html_file
		file_name = base_file_name + str(package) + "/" + html_file
		classes = get_classes(file_name)
		#pprint.pprint(classes)
		for class_ in classes.keys():
			#print("class", class_)
			file_name = base_file_name + str(package) + "/" + class_
			methods= get_methods(file_name)
			file_name = file_name + ".java.html"
			statements = get_statements(file_name, methods)
			#pprint.pprint(methods)
			#sorted_methods = sorted(methods.items(), key=lambda kv: kv[1])
			#print(sorted_methods)
			#if len(methods) != 0:
			coverage[class_] = statements
	#pprint.pprint(coverage)
	save_file(sys.argv[1], coverage);
