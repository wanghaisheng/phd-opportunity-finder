import requests
from bs4 import BeautifulSoup
import re

class NIHGrants:
    def __init__(self, keyword):
        self.keyword = keyword
        self.base_url = "https://grants.nih.gov/funding/searchguide/index.html"
        self.query_url = f"{self.base_url}?query={self.keyword.replace(' ', '+')}&x=0&y=0#/"

    def fetch_html_content(self):
        response = requests.get(self.query_url)
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
            response = requests.get(link)
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

if __name__ == "__main__":
    keyword = "wearable"  # Change this to your desired keyword
    nih_grants = NIHGrants(keyword)
    nih_grants.run()
