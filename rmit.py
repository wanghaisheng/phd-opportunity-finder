import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

class NIHGrants:
    def __init__(self, keyword, proxy=None):
        self.keyword = keyword
        self.base_url = "https://grants.nih.gov/funding/searchguide/index.html"
        self.query_url = f"{self.base_url}?query={self.keyword.replace(' ', '+')}&x=0&y=0#/"
        self.proxy = proxy  # Store proxy

    def fetch_html_content(self):
        response = requests.get(self.query_url, proxies=self.proxy)
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to retrieve content")
            return None

    def find_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            if self.keyword.lower() in a.text.lower():
                links.append(a['href'])
        return links

    def extract_text_and_email(self, link):
        try:
            response = requests.get(link, proxies=self.proxy)  # Use proxy here
            if response.status_code == 200:
                page_content = response.text
                page_soup = BeautifulSoup(page_content, 'html.parser')
                text = page_soup.get_text()
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                return text, emails
            else:
                print(f"Failed to retrieve {link}")
                return None, None
        except Exception as e:
            print(f"Error accessing {link}: {e}")
            return None, None

    def run(self):
        html_content = self.fetch_html_content()
        if html_content:
            links = self.find_links(html_content)
            print("Found Links:")
            for link in links:
                print(link)
                text, emails = self.extract_text_and_email(link)
                if text is not None:
                    print(f"\nText from {link}:\n{text[:200]}...")  # Print first 200 characters of text
                    print(f"Emails found: {emails}")

    def scrape_emails_from_pages(self, base_page_url, total_pages):
        all_emails = []
        for page in range(0, total_pages + 1):
            print(f"Scraping page {page}...")
            url=None
            if page==0:
                url=base_page_url
            else:
                url=f"{base_page_url}?page={page}"
            response = requests.get(url, proxies=self.proxy)  # Use proxy here
            if response.status_code == 200:
                page_content = response.text
                soup = BeautifulSoup(page_content, 'html.parser')
                emails = []

                # print(f"Debug: Page {page} content:\n{page_content}")  # Print first 500 characters
                for li in soup.find_all('li', class_='email'):
                    email_parts = li.find('a').contents  # Get the contents of the <a> tag
                    if email_parts:
                        local_part = email_parts[0]  # The part before the '@'
                        domain_part = ''.join(str(part) for part in email_parts[1:])  # The parts after the '@'
                        full_email = f"{local_part}@{domain_part}"
                        emails.append(full_email)

                all_emails.extend(emails)
                print('found email',len(emails))
            else:
                print(f"Failed to retrieve page {page}")
        
        # Save emails to CSV
        self.save_emails_to_csv(all_emails)

    def save_emails_to_csv(self, emails):
        df = pd.DataFrame(emails, columns=["Email"])
        df.to_csv("emails.csv", index=False)
        print("Emails saved to emails.csv")

if __name__ == "__main__":
    keyword = "wearable"  # Change this to your desired keyword
    proxy = {
        "http": "socks5://127.0.0.1:1080",  # Replace with your proxy
        "https": "socks5://127.0.0.1:1080"  # Replace with your proxy
    }
    nih_grants = NIHGrants(keyword, proxy)
    nih_grants.run()

    # Scrape emails from the specified URL
    base_page_url = "https://researchers.mq.edu.au/en/organisations/australian-institute-of-health-innovations/persons"
    total_pages = 3  # Total number of pages to scrape
    nih_grants.scrape_emails_from_pages(base_page_url, total_pages)
