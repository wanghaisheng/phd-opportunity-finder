import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import logging
from urllib.parse import quote  # Import quote for URL encoding

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your SOCKS5 proxy settings
proxies = {
    "http": "socks5://127.0.0.1:1080",  # Replace with your proxy
    "https": "socks5://127.0.0.1:1080",  # Replace with your proxy
}

# Function to construct the search URL
def construct_search_url(keyword):
    # Replace spaces with '+'
    formatted_keyword = keyword.replace(" ", "+")
    # Construct the search URL
    search_url = f"https://searchworks.stanford.edu/?f%5Bstanford_work_facet_hsim%5D%5B%5D=Thesis%2FDissertation&per_page=100&q={formatted_keyword}&search_field=search&sort=year-desc"
    return search_url

# Function to search for contributors
def search_contributors(keyword):
    search_url = construct_search_url(keyword)
    logging.debug(f"Searching for keyword: {keyword}")
    
    response = requests.get(search_url, proxies=proxies)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve search results: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    contributors = []
    
    # Find all thesis links
    for article in soup.select('article[data-document-id]'):
        # Extract the document ID
        document_id = article['data-document-id']
        # Construct the article URL
        article_url = f"https://searchworks.stanford.edu/view/{document_id}"
        logging.debug(f"Found thesis link: {article_url}")

        # Get the content of the article URL
        thesis_response = requests.get(article_url, proxies=proxies)
        if thesis_response.status_code != 200:
            logging.error(f"Failed to retrieve thesis page: {article_url} - Status code: {thesis_response.status_code}")
            continue

        thesis_soup = BeautifulSoup(thesis_response.text, 'html.parser')

        # Extract contributors from the section-body
        section_body = thesis_soup.select_one('.section-body')
        if section_body:
            contributor_elements = section_body.find_all('dt', string='Contributor')
            for contributor in contributor_elements:
                # Get the next <dd> siblings which contain the contributor links
                for dd in contributor.find_next_siblings('dd'):
                    # Extract all anchor tags within the <dd>
                    for link in dd.find_all('a'):
                        contributor_name = link.get_text(strip=True)
                        if 'University' in contributor_name:
                            continue
                        contributors.append(contributor_name)
                        logging.debug(f"Extracted contributor: {contributor_name}")

    return contributors

# Function to search Google for Stanford profiles
def search_google_for_profile(name):
    encoded_name = quote(name)  # URL encode the name

    google_search_url = f"https://www.google.com/search?q={encoded_name}+stanford"
    logging.debug(f"Searching Google for profile: {name}")
    
    response = requests.get(google_search_url, proxies=proxies)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve Google search results: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    profile_url = None
    
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and "https://profiles.stanford.edu/" in href:
            profile_url = href.split('?q=')[-1].split('&')[0].split('%3F')[0]
            logging.debug(f"Found profile URL: {profile_url}")
            break

    if not profile_url:
        logging.warning(f"No Stanford profile found for: {name}")

    return profile_url
import requests
from bs4 import BeautifulSoup
def get_bio_info(profile_url):
    bio_url = profile_url+"?tab=bio"
    response = requests.get(bio_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract bio information
    bio_content = soup.find('div', id='bioContent')
    if bio_content:  # Check if bio_content is found
        bio_text = bio_content.get_text(strip=True)  # Get the text content
    else:
        bio_text = "Bio not found"

    return bio_text

# Example usage
def get_research_info(profile_url):
    research_url = profile_url+"?tab=research-and-scholarship"
    response = requests.get(research_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract research information
    research_interests = []
    interests_section = soup.find('div', id='researchInterestTopicsContent')
    if interests_section:
        for item in interests_section.find_all('div', class_='description bulleted'):
            research_interests.append(item.get_text(strip=True))

    current_research = ""
    current_research_section = soup.find('div', id='currentResearchAndScholarlyInterestsContent')

    if current_research_section:
        current_research = current_research_section.find('p').get_text(strip=True)  # Get the text content of the <p> tag

    return research_interests,current_research

def get_email_info(profile_url):
    bio_url = profile_url+"?tab=bio"
    response = requests.get(bio_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    email=None
    # Extract email information
    contact_info = soup.find('div', id='contactInfoContent')
    if contact_info:  # Check if contact_info is found
        academic_section = contact_info.find('span', string='Academic')
        if academic_section:
            academic_div = academic_section.find_parent('div')
            email_link = academic_div.find('a', href=True)
            if email_link and 'mailto:' in email_link['href']:  # Check if it's a mailto link
                email = email_link.get_text(strip=True)  # Get the email text


        else:
            email = "Email not found"
    else:
        email = "Contact info not found"


    return email

# Example usage
# Function to extract email and research information from Stanford profile
def extract_profile_info(profile_url):
    logging.debug(f"Extracting profile info from: {profile_url}")
    research_interests,current_research = get_research_info(profile_url)
    email = get_email_info(profile_url)
    bio=get_bio_info(profile_url)
    
    return email, research_interests,current_research,bio

# Main function
def main():
    keyword = "electric health record"
    # keyword='smart watch'
    contributors = search_contributors(keyword)
    results = []

    for contributor in contributors:
        logging.info(f"Searching for {contributor}...")
        profile_url = search_google_for_profile(contributor)
        if profile_url:
            email,research_interests, current_research,bio = extract_profile_info(profile_url)
            results.append({
                'Name': contributor,
                'Profile URL': profile_url,
                'Email': email,
                'research_interests':research_interests,
                'current_research': current_research,
                'bio':bio
            })
        time.sleep(2)  # Be respectful to the server

    # Save results to Excel
    df = pd.DataFrame(results)
    df.to_csv(keyword.replace(' ','-')+'-stanford_profiles.csv', index=False)
    logging.info("Results saved to 'stanford_profiles.csv'.")

if __name__ == "__main__":
    main()
