# APICIA: An API Change Impact Analyzer for Android Apps

APICIA is a tool that analyzes the impact of updating the target API in Android apps and reports affected program elements (such as classes, methods, and statements), affected tests, and also untested affected code. It leverages API differences between API levels and applies static analysis of app source code to locate API usages for compatibility issue detection. Given the two API levels involved in an API update, APICIA first analyzes the differences of two API levels, and summarizes them into a set of API changes. Then it analyzes the source code of an app to identify the affected app code using the API changes. After that it collects coverage information of each test, and use it to identify the affected tests and their associated affected app code. Finally it identifies untested affected app code, which is affected by the API update but is not tested by existing tests.

## Prerequisites
- Python 3.8
- Java version 8
- Boost Graph Library (1.66.0)

## Python Requirements
- beautifulsoup4>=4.6.3
- graphviz>=0.9
- matplotlib>=3.0.2
- numpy>=1.15.2

## How to run
- If you do not have the requirements installed in python: run "pip install -r requirements.txt" to install all the requirements
- Within the app, first identify the folder where the app code and the tests are localized, i.e., "android/src/main/java/" and "android/src/test/java/", where the Jacoco store its coverage reports, i.e., "android/build/reports/jacoco/jacocoUnitTestReport/html/" and the targetSDKVersion of the app which is 26 for this app.
- To run: "python apicia.py <--app path--> <--source code path--> <--test path--> <--Jacoco report path--> <--current targetSDKVersion--> <--new targetSDKVersion-->", i.e., "python apicia.py example/FAST/ android/src/main/java android/src/test/java android/build/reports/jacoco/jacocoUnitTestReport/html/ 26 32"
- The output will be shown in the console as well as saved in the "apicia_output.txt" file.

## Datasets
The datasets used in the conference paper published in COMPSAC2021 are available at [https://userweb.cs.txstate.edu/~t_m386/apicia.html](https://userweb.cs.txstate.edu/~t_m386/apicia.html)
