from selenium import webdriver
from selenium.webdriver.support.ui import Select
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from collections import defaultdict


class PittClassSearch:
    def __init__(self, course):
        # initialize headless chrome driver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        # seperate course name and number
        self.courseName = course.split()[0].upper()
        self.courseNumber = course.split()[1]

        # indicates wether the query is valid
        self.valid = False
        # use selenium to search for the course and return divs containg the search results
        divs = self.searchClass(driver)
        # if the search returned a result
        if(len(divs) > 0):
            # parse the divs and fill dictionary
            self.profDict = self.parseDivs(divs)
            self.valid = True

        driver.quit()

    def searchClass(self, driver):
        driver.get("https://psmobile.pitt.edu/app/catalog/classSearch")
        # fill in course number
        driver.find_element_by_id('catalog-nbr').send_keys(self.courseNumber)
        # fill in subject
        select = Select(driver.find_element_by_name('subject'))
        select.select_by_value(self.courseName)
        # Pick Pittsburgh Campus
        select = Select(driver.find_element_by_name('campus'))
        select.select_by_value("PIT")
        # Pick fall term
        select = Select(driver.find_element_by_name('term'))
        select.select_by_value("2211")
        # click search button
        driver.find_element_by_id('buttonSearch').click()
        # wait until page is loaded, waits maximum of 15 seconds
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".primary-head")))
        # contains divs containing each of the availabe courses
        courseDivs = driver.find_elements_by_css_selector(
            '#search-results .section-content')
        return courseDivs

    def parseDivs(self, courseDivs):
        # prof dict: {instructor<str> -> {course attrbute<str> -> [course attribute values]<str>}}
        profDict = defaultdict(dict)
        # extract course info from each div
        # only lectures, no labs
        for x in courseDivs:
            # extracts class number if it is a lecture
            title = x.find_element_by_css_selector('.strong.section-body').text

            # skip lab sections and recitations
            if(title.find('LAB') != -1 or title.find('REC') != -1):
                continue

            rest = x.find_elements_by_css_selector('.section-body')

            # first element is class number which has already been added to temp
            rest.pop(0)
            rest.pop(0)  # first element is unimportant

            # extract prof name, unless it is staff
            if(rest[2].text.find("Staff") == -1):
                profNames = rest[2].text.split()
                profName = profNames[1] + " " + profNames[2]
                if(profName[len(profName)-1] == ','):
                    profName = profName[:-1]

            # add staff
            else:
                profName = "Staff"

            # fill profDict

            # append to list if duplicate professor
            if(profName in profDict.keys()):
                profDict[profName]['days/times'].append(rest[0].text[12:])
                profDict[profName]['room'].append(rest[1].text[6:])
                profDict[profName]['meeting dates'].append(rest[3].text[15:])
                profDict[profName]['class number'].append(title[title.find(
                    "(")+1:title.find(")")])

            # initialize
            else:
                profDict[profName]['days/times'] = [rest[0].text[12:]]
                profDict[profName]['room'] = [rest[1].text[6:]]
                profDict[profName]['meeting dates'] = [rest[3].text[15:]]
                profDict[profName]['class number'] = [title[title.find(
                    "(")+1:title.find(")")]]

        return profDict

    def getProfDict(self):
        return self.profDict

    def isValid(self):
        return self.valid
