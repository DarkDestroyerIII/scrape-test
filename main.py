import requests
import threading
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin

def normalize_url(url):
    """
    Normalize a URL by removing redundant double slashes and handling cases without '://'.
    """
    if "://" in url:
        parts = url.split("://", 1)  # Split once on "://"
        normalized = parts[0] + "://" + parts[1].replace("//", "/")
    else:
        normalized = url.replace("//", "/")
    return normalized

def find_emails(soup, url, emails_found):
    """
    Find and store emails found in the soup object.
    """
    email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    emails = email_pattern.findall(str(soup))
    for email in set(emails):  # Use set to avoid duplicates
        if email not in emails_found:
            emails_found[email] = url

def find_links(soup, base_url):
    """
    Extract and normalize links from the soup object.
    """
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)  # Resolve relative URLs
        full_url = normalize_url(full_url)  # Normalize the URL
        if full_url.startswith(base_url):
            links.append(full_url)
    return links

def scrape_site(url, base_url, visited_urls, emails_found, depth=0, max_depth=3):
    url = normalize_url(url)
   # print(f"Processing {url}, Depth: {depth}")

    if url in visited_urls or depth > max_depth:
        return
    visited_urls[url] = True
    print(f"Scraping {url} at depth {depth}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers, allow_redirects=True)
        final_url = normalize_url(response.url)  # Normalize after redirects

        # Check if the final URL (after any redirects) has already been visited
       
        if final_url in visited_urls:
            return
        visited_urls[final_url] = True

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            find_emails(soup, final_url, emails_found)
            links = find_links(soup, base_url)
            print(f"Found {len(links)} links")
            for link in links:
                scrape_site(link, base_url, visited_urls, emails_found, depth+1, max_depth)
    except requests.RequestException as e:
        print(f"Failed to make a request to {url}: {e}")

def main(start_url, max_depth=3):
    parsed_url = urlparse(start_url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc
    emails_found = {}
    visited_urls = {}

    scrape_site(start_url, base_url, visited_urls, emails_found, 0, max_depth)

    # Writing emails to a file
  
    with open('emails_found.txt', 'a') as file:
        for email, page in emails_found.items():
            file.write(f"Found on: {page}\n{email}\n\n")

if __name__ == "__main__":
    #start_url = "https://sallymorinlaw.com"
    urls = {"https://www.kashlegal.com","https://www.arashlaw.com","https://www.eyllaw.com"}
    #for i in urls:
main("https://www.kashlegal.com", max_depth=5)
