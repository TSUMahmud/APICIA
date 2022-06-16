import sys, os
import shutil

# path = sys.argv[2];
root = "/home/assassin/StudioProjects/Anki-Android/AnkiDroid/src/test"

def get_files(root):
	file_list = [];
	for r, d, f in os.walk(root):
		for file in f:
			if ".java" in file:
				# print (os.path.join(r, file));
				file_list.append(os.path.join(r, file));

	return file_list;

def separate(path):
	mixed_list = path.split("/");
	filename = mixed_list[-1];
	dir_tree = "";
	for m in range(0, len(mixed_list)-1):
		dir_tree = dir_tree + mixed_list[m] + "/";

	return dir_tree, filename;

def sep_list(file_list):
	l = [];
	for f in file_list:
		l.append(separate(f));
 
	return l;

def calculate_dependencies(file_list):
	dep_map = {};

	for f in file_list:
		if "extends" in f:
			flist = f.split("\n");
			for line in flist:
				if "extends" in line:
					l = line.split(" ");
					for i in range(0, len(l)):
						if l[i] == "extends":
							src_file = l[i-1];
							dpt_on = l[i+1].strip("{");

def copy_file_recur(file):
	


def read_all_files(path_list):
	for codefile in path_list:
		handle = open(codefile, "r");
		src_file = handle.read();

# def map_files(root):
# 	map_dict = {};
file_list = get_files(root);
dir_file_list = sep_list(file_list);

# next iterate over each file separately

# and then call gradle script of running test cases

# first create a temp directory
testpath = "/home/assassin/Desktop/temp/";

# print (type(sys.argv[1]))
# then move all test files to the temp directory
if sys.argv[1] == "1":
	os.makedirs(testpath, exist_ok=True);
	shutil.move(root, testpath);


	# update the new src path i.e. the testpath variable
	src_testpath = testpath + root.split("/")[-1]; 


	# now we need the new path of each file in the tree
	test_files_in_temp_list = get_files(src_testpath);
	print (test_files_in_temp_list);

	#test copying one file
	try:
		shutil.copy2(test_files_in_temp_list[0], dir_file_list[0][0]);	
	except Exception as e:
		os.makedirs(dir_file_list[0][0]);
		shutil.copy2(test_files_in_temp_list[0], dir_file_list[0][0]);	
	# iterate over the list of files
	# for (d, f) in dir_file_list:
	# 	print ()
	# print (separate(file_list[0]));
	# testdir, testfile = separate(file_list[0]);
	# print (dir_file_list);

	# move test files to temp directory

	# dir_name = root.split("/")[-1];
	#start coping files one by one


#the following line of code is to just restore files for testing the script\
if sys.argv[1] == "2":
	shutil.move(testpath + root.split("/")[-1], root);


