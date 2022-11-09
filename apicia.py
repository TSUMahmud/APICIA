import sys, re, os, pickle, pprint, operator, csv,glob2, time, ntpath

def get_files(path):
	info = os.walk(path);
	fs = [];
	for dirpath, dirname, filenames in info:
		fs += [dirpath+'/'+f for f in filenames];
	return fs;
def loadfile(filename):
	try:
		file = open(filename, 'rb');
		dict = pickle.load(file);
		file.close();
		return dict;
	except:
		return 0;

def save_file(filename, dict):
	file = open(filename, 'wb+');
	pickle.dump(dict, file);
	file.close();

def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "" # so we will return empty to remove the comment
        else: # otherwise, we will return the 1st group
            return match.group(1) # captured quoted-string
    return regex.sub(_replacer, string)

def save_sep_tests(tfiles):
	tests = [];
	for tfile in tfiles:
		className = ntpath.basename(tfile)
		strg = className.split(".")
		className = strg[0]
		handle = open(tfile, encoding="utf8");
		content = handle.read()
		content = remove_comments(content)
		content = content.split("@Test")
		if len(content) > 1:
			pkg_content = content[0]
			lines = pkg_content.split("\n");
			for i in lines:
				pkg_name_line=""
				if 'package' in i:
					pkg_name_line = i;
					pkg_name_line = pkg_name_line.strip('package')
					pkg_name_line = pkg_name_line.strip(' ')
					pkg_name_line = pkg_name_line.strip(';')
					# print(pkg_name_line);
					break;
			content = content[1:]
			# print (tfile)
			for i in content:
				# print (i)
				test_method = i.split("\n");
				test_name_line=""
				for tm in test_method:
					if 'public' in tm or 'private' in tm:
						test_name_line = tm;
						break;
				test_name = test_name_line.split(" ")
				final_name = "";
				for tn in test_name:
					if "(" in tn and ")" in tn:
						final_name = tn;
						break;
				final_name = re.sub(r'\([^)]*\)', '', final_name);
				final_name = final_name.strip('{');
				if (final_name != ""):
					classMethiod = pkg_name_line + "." + className + "." + final_name
					# classMethiod = className + "." + final_name
					tests.append(classMethiod);
	return tests;

if __name__ == '__main__':
	start_time = time.time();
	#sourcePath = ""
	appPath = "example/FAST/android/"
	srcPath = appPath + "src/main/java"
	TestsPath = appPath + "src/test/java"
	coverage_report_path =  appPath + "build/reports/jacoco/jacocoUnitTestReport/html/"
	testFiles =  get_files(TestsPath)

	tests= save_sep_tests(testFiles)
	os.system("python stats_old.py " + srcPath + " web_output.txt");
	imp_methods = loadfile("stat_output.txt")
	
	print("Impacted methods:", len(list(set(imp_methods))));
	print("Total tests:", len(list(set(tests))));
	test_time = {}
	tests_to_run = []
	time_to_run_all_tests = 0.00;
	time_to_run_selected_tests = 0.00;
	i = 0;
	j = 0;
	for test in tests:
		i = i + 1;
		print("Number:", i);
		os.chdir("example/FAST")
		test_start_time = time.time();
		print("Test: ", test);
		# os.system("gradle testDebugUnitTest --tests=" + test + " jacocoUnitTestReport")
		os.system("gradle testForGooglePlayNoExtrasDebugUnitTest --tests=" + test + " jacocoUnitTestReport")
		test_time[test] = time.time() - test_start_time
		os.chdir("../..")
		# os.system("python coverage/coverage_scraper.py gnucash-tests/" + test + ".txt")
		os.system("python coverage/coverage_scraper_old.py tests/" + test + ".txt " + coverage_report_path)

		time_to_run_all_tests = time_to_run_all_tests + test_time[test];
		
		covered= loadfile("tests/" + test + ".txt")
		flag = 0;
		if (covered == 0) :
			continue;
		for class_, methods in covered.items():
			for method_ in methods:
				method = class_ + "->" + method_;
				# print(statement);
				if (method in imp_methods):
					tests_to_run.append(test)
					time_to_run_selected_tests = time_to_run_selected_tests + test_time[test];
					print("Selected: ", method);
					j = j + 1;
					flag = 1;
					break;
			if(flag == 1):
				break;
		
		print("selected tests:", j);
	
	total_time = time.time() - start_time;
	print("Selected Tests:");
	pprint.pprint(list(set(tests_to_run)));
	print("Total time: ", total_time);
	print("Total tests:", len(list(set(tests))));
	print("Time to run all tests: ", time_to_run_all_tests);
	print("Total tests to run:", len(list(set(tests_to_run))));
	print("Time to run selected tests: ", time_to_run_selected_tests);
	
