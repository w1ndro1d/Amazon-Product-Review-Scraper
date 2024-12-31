import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Initialize WebDriver
def init_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Retrieve product names and review links from the category page
def get_product_links(driver, url):
    driver.get(url)
    time.sleep(5)  # Wait for page to load, adjust as necessary

    product_links = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
    
    for element in product_elements:
        product_links.append(element.get_attribute("href"))

    return product_links

# Extract product name and reviews from the product page
def extract_product_reviews(driver, product_link):
    driver.get(product_link)
    time.sleep(10)  # Wait for page to load, adjust as necessary

    # Extract product name
    product_name = driver.find_element(By.ID, "productTitle").text.strip()

    # Extract ASIN from URL
    # asin = product_link.split('/dp/')[1].split('/')[0] if '/dp/' in product_link else 'N/A'
    asin = driver.current_url.split('/dp/')[1].split('/')[0] if '/dp/' in driver.current_url else 'N/A'


    # Extract Price
    try:
        price = driver.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
    except Exception:
        price = "N/A"  # Price not found

    # ----------------------------get reviews----------------------
    # # Click "See more reviews" link
    # see_more_reviews_link = driver.find_element(By.CSS_SELECTOR, "a-expander-content reviewText review-text-content a-expander-partial-collapse-content")
    # driver.get(see_more_reviews_link.get_attribute("href"))
    # time.sleep(10)  # Wait for page to load, adjust as necessary

    # reviews = []
    # review_elements = driver.find_elements(By.CSS_SELECTOR, ".a-expander-content.reviewText.review-text-content.a-expander-partial-collapse-content.a-expander-content-expanded")
    # for review_element in review_elements:
    #     review_text = review_element.find_element(By.CSS_SELECTOR, "span[data-hook='review-body']").text.strip()
    #     reviews.append(review_text)

    return product_name, asin, price, 'N/A' #reviews defaulted to N/A

# Scrape data and dump to a CSV
def main():
    # URL of the category page
    category_url = 'https://www.amazon.in/s?k=gaming+laptops'
    driver = init_driver()
    product_links = get_product_links(driver, category_url)

    all_data = []
    product_limit = 30  # Set the limit for the number of products to scrape
    product_counter = 0  # Initialize a counter for processed products

    for link in product_links:
        if product_counter >= product_limit:
            break  # Stop if the limit is reached

        try:
            product_name, asin, price, reviews = extract_product_reviews(driver, link)
            for review in reviews:
                all_data.append({
                    'Product Name': product_name,
                    'ASIN': asin,
                    'Price': price,
                    'Product Review': 'N/A' #insert reviews later
                })

            product_counter += 1  # Increment the counter after processing a product

        except Exception as e:
            print(f"Error processing {link}: {e}")
                

    df = pd.DataFrame(all_data)
    df.to_csv('1.csv', index=False)
    print("Data saved to 1.csv")
    driver.quit()

if __name__ == "__main__":
    main()