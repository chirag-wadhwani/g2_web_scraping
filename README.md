# g2_web_scraping
The python script uses web scrapping to extract the details of the companies from the www.g2.com website. The script uses Playwright for web automation and BeautifulSoup for HTML parsing. It expects a csv file containing URLs from the product page of www.g2.com and after scraping stores the data in a JSON file.

# Prerequisite
## Create a virtual environment (Optional)
If you want to create a virtal environment, please follow the below steps (for windows):
Install virtual environment
- pip install virtualenv
Create a new virtual environment
- virtualenv myenv
Activate the virtual environment
- .\myenv\Scripts\activate
If the above step fails with "The term 'virtualenv' is not recognized". Try:
- python -m .\myenv\Scripts\activate

## Intall the requirements.txt
To execute the script you will have to install a few dependencies. Navigate to g2_web_scraping > g2_web_scrape and install the requirements.txt.
- cd g2_webscraping\g2_web_scrape
- pip install -r requirements.txt

# Usage
## Create input file
Create a CSV file named g2_urls.csv. This file should contain a column named "urls" and URLs from the product page of www.g2.com as its rows. Note: This file should be stored inside g2_web_scrape (g2_web_scraping > g2_web_scrape > g2_urls.csv).
## Execute the script
To execute the script, navigate to the folder where web_scraper.py file is located (g2_web_scraping > g2_web_scrape) and run the below command.
- python web_scrape.py
## Validate the result
After executing the script, a JSON file named "company_details.json" will be created in the current working directory containg the extracted data of the provided URLs.
Note: The script extracts the following details:
- Company name
- Description
- Review count
- Rating
- Rating wise review count
- Website