from selenium_utils import SeleniumUtils
from google_utils import detect_logos_uri, detect_logos_filepath, getGoogleResultFromKeyword
from pprint import pprint

def main():
    # MALICIOUS WEBSITES BELOW
    # url = 'http://www.royalmail.com.ryn.icu/invoice/redelivery/6763609117/'
    # url = 'http://crouchfamilymedicine.net/'

    # Safe websites below
    # url = 'https://wikipedia.org'
    url = 'https://www.att.com/'

    # Logo Image Processing
    su = SeleniumUtils(True)
    su.visitURL(url)
    loadedImageURLs = su.getLoadedImageURLs(url)
    print("Selenium Results")
    print(loadedImageURLs)
    print("Saving screenshots...")
    su.saveScreenshot()
    print("Saved screenshots.")
    # for image_url in loadedImageURLs:
    #     image_url_search_results_words, image_url_search_results_all = su.reverseImageSearchByURL(image_url)
    #     print('-----------')
    #     print(f"URL: [{image_url}]")
    #     pprint(image_url_search_results_words)
    #     print()
        

    # Use Vision API on the url screenshot
    screenshotLogos = detect_logos_filepath('./screenshots/url_screenshot.png')
    
    # Use Vision API on the logos
    loadedImageLogosForURLs = [detect_logos_uri(imageURL) for imageURL in loadedImageURLs]
        
    print("Google Results on URL screenshot:")
    print(screenshotLogos)
    print()
    for idx, imageURL in enumerate(loadedImageURLs):
        print(f"Google Results on logo image link {imageURL}:")
        print(loadedImageLogosForURLs[idx])

    if not screenshotLogos and not loadedImageURLs:
        print("Result:\nInconclusive. No logos found. Additional Inquiry Required.")
        exit()

    # Link Connectivity
    safe_websites = set()
    safe_websites_reachable = set()
    for screenshotLogo in screenshotLogos:
        safe_screenshot_logo_website = getGoogleResultFromKeyword(screenshotLogo)[0]
        safe_websites.add(safe_screenshot_logo_website)
        safe_websites_reachable.update(su.getWebsiteReachability(safe_screenshot_logo_website, 1))
    
    for loadedImageLogosForURL in loadedImageLogosForURLs:
        for loadedImageLogo in loadedImageLogosForURL:
            safe_loaded_image_logo_website = getGoogleResultFromKeyword(loadedImageLogo)[0]
            safe_websites.add(safe_loaded_image_logo_website)
            safe_websites_reachable.update(su.getWebsiteReachability(safe_loaded_image_logo_website, 1))
    
    unsafe_websites_reachable = set()
    unsafe_websites_reachable.update(su.getWebsiteReachability(url, 1))

    print("Result:")
    if url in safe_websites:
        print(f"Legitimate. {url} is a known and legitimate website.")
    elif url in safe_websites_reachable:
        print(f"Likely Legitimate. {url} is reachable from a known and legitimate website.")
    else:
        for a in safe_websites_reachable:
            if a in unsafe_websites_reachable:
                print(f"Highly Suspicious. A logo on {url} has been traced to a legitimate website and {url} links to that website.")
                exit()
    
    print(f"Suspicious. A logo on {url} has been traced to a legitimate website.")


if __name__ == "__main__":
    main()
