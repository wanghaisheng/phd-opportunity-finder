import requests
from bs4 import BeautifulSoup
import csv
import re

proxies = {
    "http": "socks5://127.0.0.1:1080",  # Replace with your proxy
    "https": "socks5://127.0.0.1:1080",  # Replace with your proxy
}

def get_total_pages(url):
    response = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Debug: Print the full HTML response
    print("Full HTML response:")
    # print(soup.prettify())  # Show the entire HTML structure

    # Find the pagination element
    pagination = soup.find('nav', class_='pagination global-search-tab__pagination')
    
    # Debug: Print the pagination HTML
    if pagination:
        print("Pagination HTML found:")
        print(pagination.prettify())  # Show the pagination HTML structure
    else:
        print("No pagination found.")
        # return 0

    # Extract all page numbers
    page_links = soup.find_all('a', class_='pagination-item')
    print('==',len(page_links))
    total_pages = 0
    for link in page_links:
        # Check if the link contains a span with a number
        span = link.find('span')
        if span:
            try:
                page_number = int(span.get_text(strip=True))
                total_pages = max(total_pages, page_number)  # Get the maximum page number
            except ValueError:
                print(f"ValueError: Could not convert {span.get_text(strip=True)} to an integer.")
                continue

    # Debug: Print the total pages found
    print(f"Total pages found: {total_pages}")
    return total_pages

def get_faculty_urls(url, total_pages, keyword):
    faculty_urls = []
    faculty_data = []  # List to hold faculty information

    for page in range(1, total_pages + 1):
        page_url = f"{url}&pageNumber={page}"
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract faculty URLs from the search result list
        search_results = soup.find_all('ul', class_='search-result-list')
        for result in search_results:
            for item in result.find_all('a', class_='search-result'):
                faculty_url = item['href']
                full_faculty_url = f"https://medicine.yale.edu{faculty_url}"  # Construct full URL
                faculty_urls.append(full_faculty_url)
                
                # Fetch faculty details from the faculty URL
                faculty_response = requests.get(full_faculty_url)
                faculty_soup = BeautifulSoup(faculty_response.content, 'html.parser')

                # Extract faculty name
                name = faculty_soup.find('h1', class_='profile-details-header-info__name').get_text(strip=True)

                # Extract faculty title with error handling
                title_element = faculty_soup.find('span', class_='profile-details-header-info__title')
                title = title_element.get_text(strip=True) if title_element else "N/A"

                # Extract contact information
                contact_info = faculty_soup.find('article', class_='profile-details-card profile-details-card--color-mode--light-grey')
                
                if contact_info:  # Check if contact_info is found
                    address = contact_info.find('div', class_='profile-details-mailing-address profile-details-contact-header-card__address-info')
                    
                    if address:  # Check if address is found
                        # Extract address details
                        address_name = address.find('p', class_='profile-details-mailing-address__name').get_text(strip=True)
                        address_street = address.find('p', class_='profile-details-mailing-address__street').get_text(strip=True)
                        address_location = address.find('p', class_='profile-details-mailing-address__location').get_text(strip=True)
                        address_country = address.find('p', class_='profile-details-mailing-address__country').get_text(strip=True)
                    else:
                        # Handle case where address is not found
                        address_name = address_street = address_location = address_country = "N/A"
                else:
                    # Handle case where contact_info is not found
                    address_name = address_street = address_location = address_country = "N/A"

                # Use regex to find email in the entire HTML content
                html_content = faculty_response.text
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', html_content)
                email = email_match.group(0) if email_match else "N/A"

                # Append faculty information to the list
                faculty_data.append({
                    'Name': name,
                    'Title': title,
                    'Email': email,
                    'Faculty URL': full_faculty_url,
                    'Page Number': page,
                    'Address Name': address_name,
                    'Address Street': address_street,
                    'Address Location': address_location,
                    'Address Country': address_country
                })

    # Create CSV filename with prefix 'yale' and keyword
    csv_filename = f'yale_{keyword}.csv'

    # Save results to CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Title', 'Email', 'Faculty URL', 'Page Number', 'Address Name', 'Address Street', 'Address Location', 'Address Country']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # Write the header
        for data in faculty_data:
            writer.writerow(data)  # Write each faculty's data

    return faculty_urls

# Main execution
keyword='ai'
# keyword='wearable'
keyword=keyword.replace(' ','+')
base_url = f"https://medicine.yale.edu/search/?entityType=Profile&jobClass=Faculty&q={keyword}"
# total_pages = get_total_pages(base_url)
total_pages=20
print(f"Total Pages: {total_pages}")

if total_pages > 0:
    faculty_urls = get_faculty_urls(base_url, total_pages, keyword)
    print("Faculty URLs:")
    for url in faculty_urls:
        print(url)
else:
    print("No faculty URLs found due to zero pages.")
