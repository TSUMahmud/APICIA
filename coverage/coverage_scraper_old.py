import requests, pickle, sys, glob2, re, pprint

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
	methods = []
	for file in glob2.iglob(file_name, recursive=True):
		with open(file, "r") as coverage_html_file:
			soup = BeautifulSoup(coverage_html_file, 'html.parser')
		table = soup.find('table')
		body = table.find('tbody')
		for tr in body.find_all('tr'):
			ttr = tr.find('td')
			method = (ttr.text).strip()
			td =  tr.find_all('td', {'class':"ctr2"})
			if (td[0].text).strip() != '0%':
				method = re.sub(r'\(.*?\)', '', method)
				if(method != 'static {...}'):
					ms = method.split(".");
					if(len(ms) > 1):
						method = ms[len(ms) - 1]
					methods.append(method)
	methods_set = set(methods)
	return methods_set
if __name__ == "__main__":


	Covered_classes = {}
	coverage = {}

	#for file in glob.iglob("/home/jihan/Downloads/jacoco/[a-z]/*.html", recursive=True):
	#for file in glob.iglob("/home/jihan/Downloads/testingCoverage/**/Test?/index.html", recursive=True):
	# base_file_name =  "C:/Users/User/Desktop/projects/AndroidImpactAnalysis/Anki-Android-master/AnkiDroid/build/reports/jacoco/jacocoUnitTestReport/html/"
	base_file_name =  sys.argv[2];
	# base_file_name =  "C:/Users/User/Desktop/projects/AndroidImpactAnalysis/kouchat-android-master/app/build/reports/jacoco/jacocoUnitTestReport/html/"
	# base_file_name = "C:/Users/User/Desktop/projects/AndroidImpactAnalysis/gnucash-android-master/app/build/reports/jacoco/jacocoUnitTestReport/html/"
	html_file = "index.html"
	file_name = base_file_name + html_file

	packages = get_packages(file_name)
	for package in packages.keys():
		# print(package)
		#temp_file_name = base_file_name + str(package) + "/"
		#file_name = temp_file_name + html_file
		file_name = base_file_name + str(package) + "/" + html_file
		classes = get_classes(file_name)
		for class_ in classes.keys():
			file_name = base_file_name + str(package) + "/" + str(classes[class_])
			methods = get_methods(file_name)
			coverage[class_] = methods
	# pprint.pprint(coverage)
	save_file(sys.argv[1], coverage);
