import requests, pickle, sys

from bs4 import BeautifulSoup

base_url = "https://developer.android.com/sdk/api_diff/";
change_url = "/changes/changes-summary.html";
def load_file(filename):
	file = open(filename, 'rb');
	dict = pickle.load(file);
	file.close();
	return dict;


def check_api(inp):
	#inp = input("Enter the API version: ");
	#must enter an integer value
	try:
		API = int(inp);
	except ValueError:
		print ("Enter a valid integer.");
		return -1;
	#must be greater than 19, no records of versions before that
	if API < 19:
		print ("too old");
		return -1;
	else:
		url = base_url + str(API) + change_url;
		request = requests.get(url);

		if request.status_code == 404:
			print ("API not available");
			return -1;
		else:
			return request;


def get_packages_classes(request, check=0):
	soup_obj = BeautifulSoup(request.content, "lxml");
	soup_table = soup_obj.select("table");

#    soup_table_array = [];
#    for table in soup_table:
#        soup_table_array.append(str(table));

	changed_packages = [];

	# if check==1:
	# 	print (len(soup_table));
	# 	print ("here");
	for table in soup_table:
		name_ele = table.select('tr a');
		if (len(name_ele) != 0) or (name_ele is not None):
			for name in name_ele:
				if (("Removed" in str(table)) or ("Changed" in str(table))):
					if "_added" not in str(name.get('name')):
						changed_packages.append(name.get('name'));

	while None in changed_packages:
		changed_packages.remove(None);

	return changed_packages;

def add_package_to_dict(pkg_list):
	web_dict = {};
	pkg_url_list = [];
	for pkg in pkg_list:
		#if pkg in app_dict:
	  #      print ("debug : here");
		web_dict.setdefault(pkg, {});
		pkg_format = "pkg_" + pkg + ".html";
		pkg_url_list.append(pkg_format);

	return web_dict, pkg_url_list;


def get_classes(web_dict, pkg_url_list, api):
	unused_dict = {};
	# print ("Initiating dictionary population");
	# classname_from_codefile = [];
	# for _,v in app_dict.items():
	# 	for k1,_ in v.items():
	# 		classname_from_codefile.append(k1);
	# print (len(classname_from_codefile));
	# print (classname_from_codefile[0], classname_from_codefile[1])
	for pkg_url in pkg_url_list:
		
		class_dict = {};

		pkg_url_lel = "https://developer.android.com/sdk/api_diff/" + api + "/changes/" + pkg_url;
		pkg_url_trimmed = pkg_url[4:-5];
		# print ("Package: ", pkg_url_trimmed);
		pkg_rqsts = requests.get(pkg_url_lel);
		classes = get_packages_classes(pkg_rqsts);
		
		#get all changed classes later on,a nd then methods
		for c in classes:
			# print ("class: ", c);
			# for (file_id, class_id) in classname_from_codefile:
			# if c in classname_from_codefile:
			# print ("here")
			class_dict.setdefault(c, []);
			class_url = "https://developer.android.com/sdk/api_diff/" + api + "/changes/" + pkg_url_trimmed + "." + c + ".html";
			# print (class_url);
			class_rqsts = requests.get(class_url);
			methods = get_packages_classes(class_rqsts, 1);
			# print ('meth', len(methods));
			for m in methods:
				m = m.replace(pkg_url_trimmed + "." + c + ".", "");
				m = m.replace("_changed", "");
				# print ("methods of class ", c, ": ", m);
				class_dict[c].append(m);
				# print ("done with method: ", m);
		# else:
			if pkg_url_trimmed not in unused_dict:
				unused_dict.setdefault(pkg_url_trimmed, []);
			unused_dict[pkg_url_trimmed].append(c);
			# orig_pkg_name = pkg_url_trimmed.split("pkg_")[1];
			#web_dict[pkg_url_trimmed] = class_dict;
			web_dict[pkg_url_trimmed] = class_dict;
				# correct the package names by strip[ping unnecessary data
			# print ("Done with class: ", c);
		# print ("Done with Package: ", pkg_url_trimmed);
	return web_dict;

	
def save_file(filename, web_dict):
	file = open(filename, 'wb+');
	pickle.dump(web_dict, file);
	file.close();


if __name__ == "__main__":
	# if (len(sys.argv) != 2):
	# 	print ("usage: python3 web_scraper.py ");
	# 	sys.exit(1);
	# print (isinstance(sys.argv[1], str));
	# app_dict = load_file(sys.argv[1]);
#    print (app_dict);
	inp = input("Enter api version:");
	import time
	start = time.time()
	req = (check_api(inp));
	if req == -1:
		sys.exit(0);
	pkgs = get_packages_classes(req);
	print (pkgs);

	web_dict, pkg_url_list = add_package_to_dict(pkgs);
	unfiltered_web_dict = get_classes(web_dict, pkg_url_list, inp);
	# filtered_web_dict = filter_class_methods(unfiltered_web_dict, app_dict);
	end = time.time() - start;
	print (end)
	# save_file("web_output.txt", filtered_web_dict);
	save_file("web_output.txt", unfiltered_web_dict);

	# import pprint;
	# pprint.pprint(filtered_web_dict);
	#print (web_dict);
	#print ("-----------------------\n", pkg_url_list);
	#print (app_dict);
	#for k,v in app_dict.items():
	 #   for k1,v1 in v.items():
	  #      print(k1, v1);


