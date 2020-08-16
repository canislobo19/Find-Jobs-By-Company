import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
import datetime
from random import randint
import traceback
import re


def sleepPlease():
    sleep(0.1)
    sleep(randint(0, 2))
    return None


def getSearchURLs(searchTerms, filters):
    res = []
    driver = webdriver.Chrome()
    driver.get('https://www.glassdoor.ca/Job/canada-jobs-SRCH_IL.0,6_IN3.htm')
    sleepPlease()

    for searchTerm in searchTerms:
        sleepPlease()
        sleepPlease()
        inputElement = driver.find_element_by_id("sc.keyword")
        inputElement.clear()
        sleep(0.1)
        inputElement.send_keys(searchTerm)
        inputElement.send_keys(Keys.ENTER)
        sleep(0.1)
        res.append(driver.current_url + filters)
        sleep(0.1)

    return res


def downloadCSV(result, file):
    keys = result[0].keys()
    with open('D:/Python Projects/Job Finder/jobCSVs/' + file, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(result)


def extractJobs(URL):
    try:
        # Navigate to the URL and pull all the jobs on it
        print(URL)
        if "_IP" in URL:
            currentPage = int(re.search("_IP([\d]*)", URL).group(1))
        else:
            currentPage = 1
        jobListPage = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'})
        sleepPlease()
        soupJobListPage = BeautifulSoup(jobListPage.text, "html.parser")

        allJobMetaData = soupJobListPage.find_all(name="div", attrs={"class": "jobContainer"})

        # Get the max number of pages we can search through
        PageHTML = soupJobListPage.find(name="div", attrs={"class": "cell middle hideMob padVertSm"}).get_text()
        splitPages = PageHTML.split()
        nextPage = currentPage + 1
        totalPages = int(splitPages[3])

        # For every job on the page, do this loop
        for j, div in enumerate(allJobMetaData, start=0):
            while True:
                try:
                    company = div.find_all(name="a", attrs={"class": "jobTitle"})[0].get_text()
                    jobLink = "https://www.glassdoor.ca/" + str(div.find_all(name="a", attrs={"class": "jobTitle"})[1]["href"])
                    # Get job  details and a link to the job application page
                    jobMetaData = {
                        "companyName": company,
                        "jobTitle": div.find_all(name="a", attrs={"class": "jobTitle"})[1].get_text(),
                        "location": div.find(name="span", attrs={"class": "loc"}).get_text(),
                        "applicationLink": jobLink
                    }

                    # Enter if I don't already have this job stored and it is not in the exclude list...
                    # if ("paid" not in jobMetaData["companyName"]) and (jobMetaData["companyName"] in companyList) and not any((excluded[1] == jobMetaData["jobTitle"] and excluded[0] == jobMetaData["companyName"]) for excluded in excludeList):
                    if ("paid" not in jobMetaData["companyName"]) and (jobMetaData["companyName"] in companyList):
                        # If I already have a job stored from the same company, store the new one immediately since the company already passed my criteria.
                        if any(storedJob["companyName"] == jobMetaData["companyName"] for storedJob in jobDict):
                            if any(((storedJob["companyName"] == jobMetaData["companyName"]) and (storedJob["jobTitle"] == jobMetaData["jobTitle"])) for storedJob in jobDict):
                                break
                            else:
                                jobDict.append(jobMetaData)

                        # If the company hasn't been stored before, store it.
                        else:
                            jobDict.append(jobMetaData)
                    break
                except Exception as ex1:
                    print("Error 1: ", ex1)
                    sleepPlease()
                    continue

        # These statements control moving to the next page
        if (currentPage < totalPages) and (currentPage < NoOfPagesToSearch):
            if "_IP" not in URL:
                insertPosition = URL.find(".htm")
                newURL = URL[:insertPosition] + "_IP" + str(nextPage) + URL[insertPosition:]
                extractJobs(newURL)
            elif "_IP" in URL and currentPage < 10:
                insertPosition = URL.find("_IP") + 3
                newURL = URL[:insertPosition] + str(nextPage) + URL[1 + insertPosition:]
                extractJobs(newURL)
            elif "_IP" in URL and currentPage >= 10:
                insertPosition = URL.find("_IP") + 3
                newURL = URL[:insertPosition] + str(nextPage) + URL[2 + insertPosition:]
                extractJobs(newURL)
        return
    except Exception as ex2:
        print("Error 2: ", ex2)
        return


inputList = [
    "engineer",
    "specialist",
    "technical",
    "cloud",
    "python"
]
companyList = [
    "Google",
    "MuleSoft",
    "Microsoft",
    "Salesforce",
    "Cisco Systems",
    "Apple",
    "DocuSign",
    "LinkedIn",
    "NVIDIA",
    "Facebook",
    "VMware",
    "Adobe",
    "SAP",
    "Slack",
    "Intel Corporation",
    "Oracle",
    "IBM",
    "Shopify",
    "Ceridian",
    "Wealthsimple",
    "Manulife",
    "Zoom Video Communications",
    "PagerDuty"
]

filterTerms = "?minRating=3.0"

NoOfPagesToSearch = 2

timeNow = datetime.datetime.now()
formattedTime = timeNow.strftime("%d") + "-" + timeNow.strftime("%b") + "-" + timeNow.strftime("%Y")
fileName = 'jobs-' + formattedTime + '.csv'

jobDict = []

URLList = getSearchURLs(inputList, filterTerms)
for jobURL in URLList:
    extractJobs(jobURL)

downloadCSV(jobDict, fileName)
