# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

# Set the executable path and initialize the chrome browser in splinter
def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now()
    }

    # Retrieve hemisphere data
    hemi_list = mars_hemispheres(browser)

    # Stop webdriver and return data
    browser.quit()
    
    return data, hemi_list


# ### Featured Text
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    # Parsing html
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


# ### Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()
    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url


# ### Mars table of facts
def mars_facts():
    # Add try/except for error handling
    try:
        # Scrapping the first table
        df = pd.read_html('http://space-facts.com/mars/')[0]
    
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


# ### Mars Hemispheres
# #### Scrappingt Hemispheres data
def mars_hemispheres(browser):
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Parsing html
    html = browser.html
    results = soup(html, 'html.parser')
    #Finding the list of hemispheres to scrap
    hemi_to_scrap=[]
    results = results.find_all('h3')
    for hemi in results:
        hemi_to_scrap.append(hemi.text)
    # List of Mars hemispheres with scraped title and full resolution image url
    hemi_list=[]
    for hemi_name in hemi_to_scrap:
        hemi_title,hemi_img_url = rech_info_hemi(hemi_name,browser)
        # Appending hemispheres list
        hemi_dict={"title":hemi_title,'img_url':hemi_img_url}
        hemi_list.append(hemi_dict)
    
    return hemi_list

# #### Hemisphere external function
def rech_info_hemi(name,browser):
    #Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Finding Cerberus link and clicking on it
    browser.is_element_present_by_text(name, wait_time=1)
    hemis_info_elem = browser.links.find_by_partial_text(name)
    hemis_info_elem.click()
    # Parsing html
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        # Finding title
        hemi_content = hemi_soup.find("div", class_='content')
        hemi_title = hemi_content.find("h2", class_='title').get_text()
        # Finding full resolution image url - 
        # .jpg selected as .tiff one cannot be displayed on Chrome
        hemi_content = hemi_soup.find("div", class_='downloads')
        hemi_img_url = hemi_content.find("a")['href']
    except AttributeError:
        return None

    return hemi_title,hemi_img_url


# If running as script, print scraped data
if __name__ == "__main__":
    print(scrape_all())

