import asyncio
import time
import urllib
import pandas
import os
import json

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class WebScraper:
    
    async def get_page_content(self, page):
        """Returns the BeautifulSoup object

        Args:
            page: The g2 URL page object
        """
        page_content = await page.content()
        page_html = BeautifulSoup(page_content, "html.parser")
        
        return page_html

    async def handle_bot_verification(self, page):
        """Bypasses the bot verification

        Args:
            page: The g2 URL page object
        """
        # Wait for the verification element to appear
        iframe = await page.wait_for_selector('iframe')
        frame = await iframe.content_frame()

        checkbox_exists = await frame.query_selector('input[type="checkbox"]') is not None
        start_time = time.time()
        count = 1
        while checkbox_exists != True:
            checkbox_exists = await frame.query_selector('input[type="checkbox"]') is not None

            if time.time() - start_time > 60:
                print(f"Waited 60 seconds for the checkbox element for bot verification. Number of attempts: {count} Exiting...")
                return False

            count += 1
            # Check for checkbox element after 2 seconds
            await asyncio.sleep(2)
            
        if checkbox_exists:
            checkbox = await frame.query_selector('input[type="checkbox"]')
            await checkbox.check()
            await asyncio.sleep(10)
            return True
        else:
            return False
        
    async def scrape_website(self, page_html):
        """Fetch the website of the company

        Args:
            page_html: The g2 URL page object

        Returns:
            str: Returns website of the company
            None: Returns None if the website is not found
        """
        try:
            div_website = page_html.find("div", string="Website")
            next_sibling = div_website.next_sibling
            website = next_sibling.get("href")
            if not website:
                return None
            website = urllib.parse.unquote(website, encoding='utf-8', errors='replace')
            return website
        except Exception as ex:
            print(f"Exception occurred while fetching the website. Exception: {ex}")
            return None
        
    async def scrape_specific_rating_count(self, page_html, rating):
        """Fetch the review count of the provided rating from the provided page_html

        Args:
            page_html: The g2 URL page object
            rating: Rating of which the count is to be fetched. Eg: 1, 2, 3, 4, 5. These are stars in terms of www.g2.com

        Returns:
            str: Returns review count of the provided rating
            None: Returns None if the review count is not found
        """
        try:
            star_input_element = page_html.find("input", type="radio", value=rating)
            next_sibling = star_input_element.next_sibling
            rating_count = next_sibling.find("div", class_="text-right")
            return rating_count.text.replace(",", "").strip()
        except Exception as ex:
            print(f"Exception occurred while fetching the count of {rating} star rating. Exception: {ex}")
            return None

    async def scrape_review_details(self, page_html):
        """Fetch the details of the company from the provided page_html

        Args:
            page_html: The g2 URL page object

        Returns:
            dict: Returns the basic information of the company.
        """
        review_details = {}

        company_name = page_html.find("meta", itemprop="itemReviewed")
        review_details["company_name"] = company_name["content"] if (company_name and company_name.get("content")) else "Unknown"
        
        review_count = page_html.find("meta", itemprop="reviewCount")
        review_details["review_count"] = review_count["content"] if (review_count and review_count.get("content")) else None
            
        rating = page_html.find("meta", itemprop="ratingValue")
        review_details["average_rating"] = rating["content"] if (rating and rating.get("content")) else None
        
        return review_details
    
    async def check_g2_url(self, url):
        """Validate the provided g2 URL to confirm if it can be handled by this scraping script or not.

        Args:
            url: Input g2 URL

        Returns:
            bool: Returns True/False based on the validation of the URL
        """
        if "g2.com" not in url:
            print(f"This code is just to scrape urls from www.g2.com. Skipping {url} URL")
            return False
        
        if "product" not in url:
            print(f"This code is just to scrape the products of www.g2.com. Skipping {url} URL")
            return False

        if "review" not in url:
            print(f"The URL should contain review. Skipping {url} URL")
            return False
        
        return True
        
    async def run_web_scrape(self, g2_urls):
        """Run the scraping for the G2 URLs.

        Args:
            g2_urls: List of G2 URLs
            
        Returns:
            bool: Returns a dictionary having key as company name and value as its detials
        """

        company_details = {}
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False, slow_mo=100)
            page = await browser.new_page()
            for url in g2_urls:
                url_validation = await self.check_g2_url(url)
                if not url_validation:
                    continue
                review_details = {}
                await page.goto(url)
                bot_verification = await self.handle_bot_verification(page)
                if not bot_verification:
                    print(f"Could not bypass the bot verification. Skipping {url} URL.")
                    continue

                try:
                    page_html = await self.get_page_content(page)
                except Exception as ex:
                    print(f"Unable to parse the content of {url} URL. Error: {ex}")
                    continue

                review_details = await self.scrape_review_details(page_html)
                review_details["website"] = await self.scrape_website(page_html)
                
                review_details["ratings"] = {}

                for rating in range(1, 6):
                    review_details["ratings"][str(rating)] = await self.scrape_specific_rating_count(page_html, str(rating))
                    
                review_details["g2_url"] = url
                company_details[review_details["company_name"]] = review_details

            return company_details

if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    filename = "g2_urls.csv"
    file_path = os.path.join(current_folder, filename)
    df = pandas.read_csv(file_path)
    g2_urls = df["urls"].tolist()

    web_scraper = WebScraper()
    company_details = asyncio.run(web_scraper.run_web_scrape(g2_urls))
    
    with open("company_details.json", "w") as f:
        json.dump(company_details, f)
