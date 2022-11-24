import sys, re, os, pickle, pprint, operator, csv, time
from matplotlib import pyplot as plt


def connected(classfile, all_minus_classfile, flag, impacted_classfiles):
    if len(all_minus_classfile) == 0:
        return flag
    else:
        for f in all_minus_classfile:
            f_class = f.split("/")[-1].split(".")[0]
            if (
                f_class in open(classfile, "r").read()
                and f_class in impacted_classfiles
            ):
                return True
            else:
                remaining_classes = all_minus_classfile[1:]
                return flag or connected(
                    f, remaining_classes, False, impacted_classfiles
                )


def get_files(path):
    info = os.walk(path)
    fs = []
    for dirpath, dirname, filenames in info:
        fs += [dirpath + "/" + f for f in filenames]
    return fs


def get_stats(dict, files):
    userclasses = {}
    pkg_x_axis = []
    pkg_y_axis = []
    pkg_y2_axis = []
    class_x_axis = []
    class_y_axis = []
    class_y2_axis = []
    method_x_axis = []
    method_y_axis = []
    method_y2_axis = []
    files = [x for x in files if ".java" in x]
    # pprint.pprint(dict);
    # print ("Total files:", len(files));
    pkgs = [p for (p, cm) in dict.items()]
    classes = [c for (_, cm) in dict.items() for (c, _) in cm.items()]
    # methods = [m for (_,cm) in dict.items() for (_,ms) in cm.items() for m in ms ];
    methods = [cm for (_, cm) in dict.items() if bool(cm)]
    # for method_name in methods:
    # 	method_name = re.sub(r'\([^)]*\)', '', method_name) + "()";
    # methods = [re.sub(r'\([^)]*\)', '', method_name) + "()" for method_name in methods];
    for cms in methods:
        for corr_class, mmethods in cms.items():
            # for mmethod in mmethods:
            mmethods = [
                re.sub(r"\([^)]*\)", "", mmethod) + "()" for mmethod in mmethods
            ]
            mmethods = list(set(mmethods))
            cms[corr_class] = mmethods

    # methods = [x for x in cms]
    # pprint.pprint (methods)
    # print ("--------------------------------------------------")

    # print (methods);
    # pcount = 0;
    # methods = list(set(methods));
    overallp = 0
    # print ("Package - ", "Number of impacted app classes - ", "Package Impact percentage");
    for p in pkgs:
        pcount = 0
        for f in files:
            handle = open(f, "r", encoding="utf8")
            if p in handle.read():
                pcount += 1
            handle.close()
        overallp += pcount
        pkg_x_axis.append(p)
        pkg_y_axis.append(pcount)
        pkg_y2_axis.append(str(round(pcount / len(files) * 100, 2)))

        # if pcount > 0:
        # print (p, pcount, str(round(pcount/len(files) * 100, 2)));

    # fig, _ = plt.subplots();
    # plt.plot(pkg_x_axis, pkg_y_axis);
    # plt.tick_params(labelsize=5);
    # fig.subplots_adjust(bottom=0.3);
    # plt.xlabel("Packages");
    # plt.ylabel("app files affected");
    # plt.xticks(rotation=90);
    # plt.savefig("");
    overallc = 0
    imp_classes = []
    # print ("Class - ", "Number of impacted app classes - ", "Class Impact percentage")
    for c in classes:
        # print(c);
        userclasses.setdefault(c, [])
        ccount = 0
        for f in files:
            handle = open(f, "r", encoding="utf8")
            if c in handle.read():
                filename = f.split("/")[-1].split(".")[0]
                userclasses[c] += [filename]
                ccount += 1
                imp_classes.append(filename)
                # if c == "Resources":
                # 	print (c);
            handle.close()
        overallc += ccount
        class_x_axis.append(c)
        class_y_axis.append(ccount)
        class_y2_axis.append(str(round(ccount / len(files) * 100, 2)))

        # if ccount > 0:
        # 	print (c,ccount,str(round(ccount/len(files) * 100, 2)));
        # print ("cls impact percentage:", );

    overallm = 0
    usermethods = {}
    # print ("Methods - ", "Number of impacted app classes - ", "Method Impact Percentage");
    meth_network = save_sep_methods(files)
    # print (meth_network)
    # input("enter to continue")
    imp_methods = []
    all_methods = []
    allmcount = 0
    for cm in methods:
        for c, m in cm.items():
            # all_methods += m
            for h in m:
                usermethods.setdefault(h, [])
                # allmcount += 1

    mcount = 0

    def find_relevant_class(files, method):
        for f in files:
            # if 'AppUtils' in f:
            # 	print (f)
            handle = open(f, "r", encoding="utf8")
            data = handle.read()
            for d in data.split("\n"):
                # print (method, 'before condition')
                if (method in d) and (
                    "public" in d or "private" in d or "static" in d or "protected" in d
                ):
                    return f.split("/")[-1].split(".")[0]

    # print(meth_network)
    for k, v in meth_network.items():
        for k2, v2 in v.items():
            all_methods.append(k2)
    for cm in methods:
        for c, ms in cm.items():
            for m in ms:
                # usermethods.setdefault(m, []);
                for _, v in meth_network.items():
                    for k2, v2 in v.items():
                        # all_methods.append(c+"->"+k2)
                        # print (m)
                        for s in v2:
                            if m[:-2] in s:
                                cl = find_relevant_class(files, k2)
                                if cl is not None:
                                    usermethods[m] += [cl + "->" + k2]
                                    mcount += 1
                                    if k2 not in "\t".join(imp_methods):
                                        imp_methods.append(cl + "->" + k2 + "->" + s)
                # for f in files:
                # 	handle = open(f, 'r');
                # 	if m[:-1] in handle.read():
                # 		filename = f.split("/")[-1].split(".")[0];
                # 		usermethods[m] += [filename];
                # 		mcount += 1;
                # 	handle.close();
                overallm += mcount
                method_x_axis.append(m)
                method_y_axis.append(mcount)
                method_y2_axis.append(str(round(mcount / len(files) * 100, 2)))

        # if mcount > 0:
        # 	print (m, mcount, str(round(mcount/len(files) * 100, 2)));
    # print (overallc, overallp);
    # print (usermethods)
    # input("continue")
    plot_data = []
    num_imp_classes = len(list(set(imp_classes)))
    total_classes = len(files)

    num_imp_methods = len(list(set(imp_methods)))
    # num_imp_methods = mcount
    # pprint.pprint(usermethods)
    # total_methods = len(list(set(all_methods)))
    total_methods = len(all_methods)
    # pprint.pprint(imp_methods)

    # for i in imp_methods:
    # 	if 'PlayStore' in i:
    # 		print (i)
    # total_methods = len(all_methods)
    # total_methods = allmcount
    # print (num_imp_methods, total_methods)

    # print (list(set(imp_methods)))
    # plot_data =[(pkg_x_axis, pkg_y_axis, pkg_y2_axis), (class_x_axis, class_y_axis, class_y2_axis), (method_x_axis, method_y_axis, method_y2_axis)];
    # total_statements = 0;
    # for f in files:
    # 	handle = open(f, 'r', encoding="utf8");
    # 	num_lines = sum(1 for line in handle);
    # 	handle.close();
    # 	total_statements = total_statements + num_lines;

    # print ("Number of impacted statements: ", num_imp_methods, "Statement Impact:", round(num_imp_methods/total_statements *100, 2))
    # print ("Total statements: ", total_statements);
    print("total classes: ", total_classes, "total methods: ", total_methods)
    return userclasses, usermethods, plot_data, imp_methods
    # print (pkgs);
    # print (methods);
    # print (classes);
    # print (userclasses);


# def count_occurence(filename):


def testmaps(testfiles, userclasses, usermethods):
    testfiles = [x for x in testfiles if ".java" in x]
    # print (len(testfiles))
    aff_tests = []
    testmap = {}
    # testmap to impacted classes
    for f in testfiles:
        handle = open(f, "r")
        k = f.split("/")[-1].split(".")[0]
        testmap.setdefault(k, [])
        filedata = handle.read()
        for changed_library_class, impacted_user_classes in userclasses.items():
            for iuc in impacted_user_classes:
                # print (handle.read())
                # print ("----------------")
                if iuc in filedata:
                    # print ("here");
                    testmap[k] += [changed_library_class]
                    aff_tests.append(k)
        testmap[k] = list(set(testmap[k]))
        handle.close()

    # pprint.pprint (userclasses);
    testmap2 = {}
    for f in testfiles:
        handle = open(f, "r")
        k = f.split("/")[-1].split(".")[0]
        testmap2.setdefault(k, [])
        filedata = handle.read()
        for changed_method, impacted_user_classes in usermethods.items():
            for iuc in impacted_user_classes:
                if iuc in filedata:
                    testmap2[k] += [changed_method]
        testmap2[k] = list(set(testmap2[k]))
        handle.close()

    # pprint.pprint (testmap);
    # pprint.pprint (testmap2);
    no_test_rerun = []
    no_test_rerun2 = []
    for k, v in testmap.items():
        if v == []:
            no_test_rerun.append(k)
    print("Unaffected test classes by library changes: ")
    print(no_test_rerun)
    print(len(testfiles))
    aff_tests = list(set(aff_tests))
    print(len(aff_tests))

    # for k,v in testmap2.items():
    # 	if v==[]:
    # 		no_test_rerun2.append(k);

    # print ("Unaffected test classes by library methods: ");
    # print (no_test_rerun2);


def loadfile(filename):
    file = open(filename, "rb")
    dict = pickle.load(file)
    file.close()
    return dict


def plot_the_stuff(plot_data):
    pkgx, pkgy, pkgy2 = plot_data[0]
    clsx, clsy, clsy2 = plot_data[1]
    mx, my, my2 = plot_data[2]

    # plt.figure(1);
    fig, _ = plt.subplots()
    plt.plot(pkgx, pkgy)
    plt.tick_params(labelsize=5)
    fig.subplots_adjust(bottom=0.3)
    plt.xlabel("Packages")
    plt.ylabel("app files affected")
    plt.xticks(rotation=90)
    plt.savefig("pkg_appfile")
    with open("pkg1.csv", "w", newline="") as myfile:
        wr = csv.writer(myfile)
        wr.writerow(pkgx)
        wr.writerow(pkgy)
    plt.clf()
    # pkgx2 = [k for k,v in sorted(zip(pkgx, pkgy2), key=operator.itemgetter(1))];
    pkgx2 = pkgx
    # pkgy2 = sorted(pkgy2);
    # fig, _ = plt.subplots();
    # plt.figure(2);
    fig, _ = plt.subplots()
    plt.plot(pkgx2, pkgy2)
    plt.tick_params(labelsize=5)
    fig.subplots_adjust(bottom=0.3)
    plt.xlabel("Packages")
    plt.ylabel("impact percentage")
    plt.xticks(rotation=90)
    plt.savefig("pkg_percent")
    with open("pkg2.csv", "w", newline="") as myfile:
        wr = csv.writer(myfile)
        wr.writerow(pkgx2)
        wr.writerow(pkgy2)

    plt.clf()
    plt.figure(figsize=(30, 10))
    fig, _ = plt.subplots()
    plt.plot(clsx, clsy)
    plt.tick_params(labelsize=5)
    fig.subplots_adjust(bottom=0.3)
    plt.xlabel("Classes")
    plt.ylabel("app files affected")
    plt.xticks(rotation=90)
    plt.savefig("cls_appfile")
    with open("cls1.csv", "w", newline="") as myfile:
        wr = csv.writer(myfile)
        wr.writerow(clsx)
        wr.writerow(clsy)
    plt.clf()
    # clsx2 = [k for k,v in sorted(zip(clsx, clsy2), key=operator.itemgetter(1))];
    clsx2 = clsx
    # clsy2 = sorted(clsy2);
    # fig, _ = plt.subplots();
    # plt.figure(2);
    fig, _ = plt.subplots()
    plt.plot(clsx2, clsy2)
    plt.tick_params(labelsize=5)
    fig.subplots_adjust(bottom=0.3)
    plt.xlabel("Classes")
    plt.ylabel("impact percentage")
    plt.xticks(rotation=90)
    plt.savefig("cls_percent")
    with open("cls2.csv", "w", newline="") as myfile:
        wr = csv.writer(myfile)
        wr.writerow(clsx2)
        wr.writerow(clsy2)
    plt.clf()
    fig, _ = plt.subplots()
    plt.plot(mx, my)
    plt.tick_params(labelsize=5)
    fig.subplots_adjust(bottom=0.3)
    plt.xlabel("Methods")
    plt.ylabel("app files affected")
    plt.xticks(rotation=90)
    plt.savefig("m_appfile")
    with open("m1.csv", "w", newline="") as myfile:
        wr = csv.writer(myfile)
        wr.writerow(mx)
        wr.writerow(my)
    plt.clf()
    # mx2 = [k for k,v in sorted(zip(mx, my2), key=operator.itemgetter(1))];
    mx2 = mx
    # my2 = sorted(my2);
    # fig, _ = plt.subplots();
    # plt.figure(2);
    fig, _ = plt.subplots()
    plt.plot(mx2, my2)
    plt.tick_params(labelsize=5)
    fig.subplots_adjust(bottom=0.3)
    plt.xlabel("Methods")
    plt.ylabel("impact percentage")
    plt.xticks(rotation=90)
    plt.savefig("m_percent")
    with open("m2.csv", "w", newline="") as myfile:
        wr = csv.writer(myfile)
        wr.writerow(mx2)
        wr.writerow(my2)


def dynamic_testmaps(testdicts, userclasses, usermethods):
    # testdicts = [x for x in testfiles if ".java" in x];
    # print (len(testfiles))
    testmap = {}
    # testmap to impacted classes
    for f in testdicts:
        # handle = open(f, 'r');
        f_dict = loadfile(f)
        k = f.split("/")[-1]
        testmap.setdefault(k, [])
        # filedata = handle.read();
        # pprint.pprint(f_dict)
        test_pkgs, test_classes, test_methods = f_dict[k]
        for changed_library_class, impacted_user_classes in userclasses.items():
            for iuc in impacted_user_classes:
                # print (handle.read())
                # print ("----------------")
                for test_class in test_classes:
                    if iuc in test_class:
                        # print ("here");
                        testmap[k] += [changed_library_class]
        testmap[k] = list(set(testmap[k]))
        # handle.close();
    print("------------------")
    print("DONE WITH CLASSES")
    print("------------------")
    # pprint.pprint (userclasses);
    testmap2 = {}
    for f in testdicts:
        # handle = open(f, 'r');
        f_dict2 = loadfile(f)
        k = f.split("/")[-1]
        testmap2.setdefault(k, [])
        test_pkgs, test_classes, test_methods = f_dict2[k]
        # filedata = handle.read();
        for changed_method, impacted_user_classes in usermethods.items():
            for iuc in impacted_user_classes:
                for test_method in test_methods:
                    if iuc in test_method:
                        testmap2[k] += [changed_method]
        testmap2[k] = list(set(testmap2[k]))
        # handle.close();

    # pprint.pprint (testmap);
    # pprint.pprint (testmap2);
    no_test_rerun = []
    no_test_rerun2 = []
    for k, v in testmap.items():
        if v == []:
            no_test_rerun.append(k)

    print("Unaffected test classes by library changes: ")
    print(no_test_rerun)

    for k, v in testmap2.items():
        if v == []:
            no_test_rerun2.append(k)

    print("Unaffected test classes by library methods: ")
    print(no_test_rerun2)

    pprint.pprint(testmap)
    pprint.pprint(testmap2)


def static_testmaps(testfiles, files, userclasses, usermethods):
    testfiles = [x for x in testfiles if ".java" in x]
    aff_test = []
    # print (len(testfiles))
    testmap = {}
    # testmap to impacted classes
    imp_classes = []
    for changed_library_class, impacted_user_classes in userclasses.items():
        for iuc in impacted_user_classes:
            imp_classes.append(iuc)
        imp_classes = list(set(imp_classes))
    for f in testfiles:
        handle = open(f, "r")
        k = f.split("/")[-1].split(".")[0]
        testmap.setdefault(k, [])
        filedata = handle.read()
        for changed_library_class, impacted_user_classes in userclasses.items():
            for iuc in impacted_user_classes:
                # print (handle.read())
                # print ("----------------")
                if iuc in filedata:
                    # print ("here");
                    testmap[k] += [changed_library_class]
                    aff_test.append(k)
                else:
                    for e in files:
                        if iuc in e:
                            newfiles = files
                            newfiles.remove(e)
                            chain = connected(e, newfiles, [], imp_classes)
                            aff_test.append(k)
        testmap[k] = list(set(testmap[k]))
        handle.close()

    aff_test = list(set(aff_test))
    # pprint.pprint (userclasses);
    testmap2 = {}
    for f in testfiles:
        handle = open(f, "r")
        k = f.split("/")[-1].split(".")[0]
        testmap2.setdefault(k, [])
        filedata = handle.read()
        for changed_method, impacted_user_classes in usermethods.items():
            for iuc in impacted_user_classes:
                if iuc in filedata:
                    testmap2[k] += [changed_method]
        testmap2[k] = list(set(testmap2[k]))
        handle.close()

    # pprint.pprint (testmap);
    # pprint.pprint (testmap2);
    no_test_rerun = []
    no_test_rerun2 = []
    for k, v in testmap.items():
        if v == []:
            no_test_rerun.append(k)
    print("Unaffected test classes by library changes: ")
    print(no_test_rerun)
    print(len(testfiles))
    print(len(aff_test))
    # for k,v in testmap2.items():
    # 	if v==[]:
    # 		no_test_rerun2.append(k);

    # print ("Unaffected test classes by library methods: ");
    # print (no_test_rerun2);


def static_testmaps2(testfiles, files, userclasses, usermethods, new_dir):
    start_time = time.time()
    testfiles = [x for x in testfiles if ".java" in x]
    sep_tests = save_sep_tests(testfiles, new_dir)
    mid_time = time.time() - start_time
    aff_test = []
    # print (len(testfiles))
    testmap = {}
    # testmap to impacted classes
    imp_classes = []
    for changed_library_class, impacted_user_classes in userclasses.items():
        for iuc in impacted_user_classes:
            imp_classes.append(iuc)
        imp_classes = list(set(imp_classes))
    for f in sep_tests:
        handle = open(f, "r")
        k = f.split("/")[-1]
        testmap.setdefault(k, [])
        filedata = handle.read()
        for changed_library_class, impacted_user_classes in userclasses.items():
            for iuc in impacted_user_classes:
                # print (handle.read())
                # print ("----------------")
                if iuc in filedata:
                    # print ("here");
                    testmap[k] += [changed_library_class]
                    aff_test.append(k)
                else:
                    for e in files:
                        if iuc in e:
                            newfiles = files
                            newfiles.remove(e)
                            chain = connected(e, newfiles, [], imp_classes)
                            if chain == True:
                                aff_test.append(k)
        testmap[k] = list(set(testmap[k]))
        handle.close()

    aff_test = list(set(aff_test))
    # pprint.pprint (userclasses);
    start_again = time.time()
    aff_test2 = []
    testmap2 = {}
    for f in sep_tests:
        handle = open(f, "r")
        k = f.split("/")[-1]
        testmap2.setdefault(k, [])
        filedata = handle.read()
        for changed_method, impacted_user_methods in usermethods.items():
            # print (impacted_user_methods)
            for ium in impacted_user_methods:
                if ium in filedata:
                    testmap2[k] += [changed_method]
                    aff_test2.append(k)
        testmap2[k] = list(set(testmap2[k]))
        handle.close()
    end_time = time.time() - start_again
    # pprint.pprint (testmap);
    # pprint.pprint (testmap2);
    no_test_rerun = []
    no_test_rerun2 = []
    for k, v in testmap.items():
        if v == []:
            no_test_rerun.append(k)
    print("Unaffected test methods by library class changes: ")
    # print(no_test_rerun);
    print(len(sep_tests))
    print(len(aff_test))

    print("Unaffected test methods by library method changes: ")
    print(len(sep_tests))
    print(len(list(set(aff_test2))))

    print("time for test impact percentage: ", mid_time + end_time)


# for k,v in testmap2.items():
# 	if v==[]:
# 		no_test_rerun2.append(k);

# print ("Unaffected test classes by library methods: ");
# print (no_test_rerun2);


def save_sep_tests(tfiles, new_dir):
    tests = []
    for tfile in tfiles:
        handle = open(tfile, "r")
        content = handle.read()
        content = remove_comments(content)
        content = content.split("@Test")
        if len(content) > 1:
            content = content[1:]
            # print (tfile)
            for i in content:
                # print (i)
                test_method = i.split("\n")
                for tm in test_method:
                    if "public" in tm or "private" in tm:
                        test_name_line = tm
                        break
                test_name = test_name_line.split(" ")
                final_name = ""
                for tn in test_name:
                    if "(" in tn and ")" in tn:
                        final_name = tn
                        break
                final_name = re.sub(r"\([^)]*\)", "", final_name)
                # print(final_name)
                # print ("--------------")
                # print (test_method);
                # print ("\n".join(test_method) == i);
                # print("--------------")
                final_name = new_dir + "/" + final_name
                write_content = "\n".join(test_method)
                with open(final_name, "w+") as write_handle:
                    tests.append(final_name)
                    write_handle.write(write_content)
    return tests


def save_sep_methods(files, new_dir=0):
    meth_network = {}
    meth_network_temp = {}
    for file in files:
        meth_network_temp.setdefault(file, {})
        meth_network.setdefault(file, {})
        handle = open(file, "r", encoding="utf8")
        content = handle.read()
        # print (content_in_lines)
        to_be_removed = re.findall(r"(@)([A-Za-z0-9]+)\(", content)
        to_be_removed = [x for (_, x) in to_be_removed]
        content = remove_comments(content)
        content_in_lines = content.split("\n")
        # content_in_lines = [x.strip("\n") for x in content_in_lines];
        content_in_lines = [x.lstrip("\t") for x in content_in_lines]
        content_in_lines = [x.lstrip(" ") for x in content_in_lines]
        # print (content)
        check = re.findall(
            r"(public|private|static) ([A-Za-z0-9<>.\[\]]+) ([A-Za-z0-9]+)\(", content
        )
        check = [x3 for (x1, x2, x3) in check]
        if len(check) is 0:
            check = re.findall(r"(public|private|static) ([A-Za-z0-9]+)\(", content)
            check = [x2 for (x1, x2) in check]
        if len(check) is 0:
            check = re.findall(r"([A-Za-z0-9<>.\[\]]+) ([A-Za-z0-9]+)\(", content)
            check = [x2 for (x1, x2) in check]
        if len(check) is 0:
            continue
        check2 = re.findall(r"([A-Za-z0-9]+)\(", content)
        # print ("----------------------------------")
        check2 = [x for x in check2 if x not in to_be_removed]
        # print (check2)

        check_index = 0
        check2_index = 0
        meth = {}
        meth2 = {}

        # calculate which method called whom
        # print (file)
        for c in check:
            meth.setdefault(c, [])
        while check2_index < (len(check2)):
            if check_index < len(check) and check[check_index] == check2[check2_index]:
                check_index += 1
            else:
                meth[check[check_index - 1]].append(check2[check2_index])
            check2_index += 1

        test2 = []
        # remove duplicates
        for k, v in meth.items():
            meth[k] = list(set(v))
            meth2.setdefault(k, [])

        meth_network_temp[file] = meth
        # print (meth_network[file])

        for mmap, methods in meth_network_temp[file].items():
        	for method in methods:
        		for codeline in content_in_lines:
        			method_name = method + "("
					if method_name in codeline:
						test2.append(codeline)
						meth2[mmap].append(codeline)
    # print (test2)

		for k,v in meth2.items():
			meth2[k] = list(set(v))

		meth_network[file] = meth2

    return meth_network


def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)


def save_file(filename, web_dict):
    file = open(filename, "wb+")
    pickle.dump(web_dict, file)
    file.close()


if __name__ == "__main__":
    files = get_files(sys.argv[1])
    # print (files);
    dic = loadfile(sys.argv[2])
    st_time = time.time()
    uc, um, plot_data, im = get_stats(dic, files)
    x_time = time.time() - st_time
    print("src code filter time: ", x_time)
    save_file("stat_output.txt", im)
    # plot_the_stuff(plot_data);
    # testfiles = get_files(sys.argv[3]);
    # testmaps(testfiles, uc, um);
    # temp_path = sys.argv[4];
    # dynamic_testmaps(testfiles, uc, um);
    # static_testmaps(testfiles, files, uc, um);
    # static_testmaps2(testfiles, files, uc, um, temp_path);
