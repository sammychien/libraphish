from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import json
from collections import Counter
import time
from selenium.webdriver import Firefox, FirefoxOptions
from pprint import pprint
import google_utils

def createDriver():
    opts = FirefoxOptions()
    opts.add_argument("--width=400")
    opts.add_argument("--height=300")
    driver = webdriver.Firefox(options=opts)
    return driver

def cleanImageURL(url):
    valid_image_extensions = ['.png', '.jpg', '.jpeg']
    for ext in valid_image_extensions:
        if ext in url:
            cleaned = url.split(ext)[0] + ext
            return cleaned
    return ''

def getGoogleReverseImageSearchURL(imageURL):
    return f"https://www.google.com/searchbyimage?sbisrc=4chanx&image_url={imageURL}&safe=off"

def getCleanedWordListFromStrings(strings):
    words = []
    for string in strings:
        # Remove non-alphabetic characters and make lowercase
        filtered_string = ''.join(x for x in string if x.isalpha() or x == ' ')
        filtered_string = filtered_string.lower()
        str_split = filtered_string.split(' ')
        words.extend(str_split)
    return words

def getMostCommonWords(words, n):
    counter = Counter(words)

    # Delete entries from filter (todo)
    filter = ['', 'error']
    for word in filter:
        if word in counter:
            del counter[word]

    most_common = counter.most_common(n)
    return [word[0] for word in most_common if word[0] not in filter]

class SeleniumUtils:
    def __init__(self, debug=False):
        print("Creating Driver")
        self.driver = createDriver()
        print("Created Driver")
        self.debug = debug

    def __del__(self):
        if (self.driver != None):
            self.driver.quit()

    def getDriver(self):
        return self.driver

    def getLoadedImageURLs(self, url):
        self.driver.get(url)
        
        # self.driver.implicitly_wait(5) # seconds
        time.sleep(10)
        timings = self.driver.execute_script("return window.performance.getEntries();")

        if self.debug:
            with open("window_performance_timings.json", "w") as f:
                json.dump(timings, f)

        # print([timing.get('name') for timing in timings if "logo" in timing.get('name')])

        loadedImageURLs = []
        valid_initiator_types = ["img", "image", "other", "imageset"]
        for timing in timings:
            if timing.get('initiatorType', "") in valid_initiator_types and "logo" in timing.get('name'):
                image_link = cleanImageURL(timing['name'])
                if image_link != '':
                    loadedImageURLs.append(image_link)

        return loadedImageURLs
    
    def visitURL(self, url):
        self.driver.get(url)

    def saveScreenshot(self):
        try:
            self.driver.get_screenshot_as_file('./screenshots/url_screenshot.png')
        except:
            print("error")

    def reverseImageSearchByURL(self, imageURL):
        googleReverseImageSearchURL = getGoogleReverseImageSearchURL(imageURL)
        self.driver.get(googleReverseImageSearchURL)

        if self.debug:
            print(f"google search url: [{googleReverseImageSearchURL}]")
            # self.driver.save_screenshot('./url_screenshot.png')

        # Wait for redirect
        # wait = WebDriverWait(driver, 10)
        # wait.until(lambda driver: driver.current_url != url)

        search_results = self.driver.find_elements(By.ID, 'search')[0].find_elements(By.XPATH, '//h3/parent::*')


        # filter = ['Visually similar images', 'Description']
        results = []
        for search_result in search_results:
            text = search_result.find_element(By.XPATH, './/h3').text
            try:
                link = search_result.find_element(By.XPATH, './/cite').get_attribute("innerHTML").splitlines()[0].split("<")[0]
            except Exception as e:
                link = ''
            results.append((text, link))

        text_strings = getCleanedWordListFromStrings([x[0] for x in results])
        most_common_words = getMostCommonWords(text_strings, 5)

        return most_common_words, results

    def getWebsiteReachability(self, baseURL, depth=3):
        
        visitedWebsites = set()
        visitedWebsites.add(baseURL)
        self.getWebsiteReachabilityRecursion(baseURL, depth, visitedWebsites)
        
        if self.debug:
            print("Visited Websites:")
            pprint(visitedWebsites)

        reducedWebsiteSet = set([google_utils.reduceURL(website) for website in visitedWebsites])
        
        return reducedWebsiteSet

    def getWebsiteReachabilityRecursion(self, baseURL, depth, visited):
        if self.debug:
            print(f"BaseURL: {baseURL}\t depth: {depth}")

        if depth == 0:
            return visited
        
        if self.driver.current_url != baseURL:
            self.visitURL(baseURL)
        linksOnPage = self.getAllLinksOnPage()
        if depth == 1:
            visited.update(linksOnPage)
            return visited

        for link in linksOnPage:
            if link not in visited:
                visited.add(link)
                self.getWebsiteReachabilityRecursion(link, depth-1, visited)


    def getAllLinksOnPage(self):
        elems = self.driver.find_elements_by_xpath("//a[@href]")
        results = set([elem.get_attribute("href") for elem in elems])
        return results

if __name__ == "__main__":
    su = SeleniumUtils(True)
    webs = su.getWebsiteReachability("https://www.google.com", 2)
    pprint(webs)


