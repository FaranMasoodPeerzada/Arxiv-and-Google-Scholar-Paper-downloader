import csv
import time
import requests
import os
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

pdf_urls = []

def download_pdfs(pdf_urls, category):
    category_dir = os.path.join("google_scholar", category)
    os.makedirs(category_dir, exist_ok=True)  # Create directory if it doesn't exist
    for idx, pdf_url in enumerate(pdf_urls):
        try:
            retries = Retry(total=3, backoff_factor=0.5)
            session = requests.Session()
            session.mount('https://', HTTPAdapter(max_retries=retries))
            response = session.get(pdf_url, stream=True)

            if response.status_code == 200:
                with open(os.path.join(category_dir, f"Google_scholar_{category}_{idx + 1}.pdf"), "wb") as f:  # Save in category directory
                    f.write(response.content)
                print(f"Downloaded paper {idx + 1} in category {category}")
            elif response.status_code == 403:
                print(f"Failed to download paper {idx + 1} in category {category}: Status code 403 (Forbidden)")
            elif response.status_code == 404:
                print(f"Failed to download paper {idx + 1} in category {category}: Status code 404 (Not Found)")
            else:
                print(f"Failed to download paper {idx + 1} in category {category}: Status code {response.status_code}")
        except Exception as e:
            print(f"Error downloading paper {idx + 1} in category {category}: {e}")

# Rest of your code remains the same

def download_paper_with_retry(url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, stream=True)
            time.sleep(5)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download paper: Status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading paper: {e}")
        retries += 1
        time.sleep(5)  # Wait for 1 second before retrying
    return None

def google_scholar_search(query, max_pages):
    for page in range(max_pages):
        start_index = page * 10
        url = f"https://scholar.google.com/scholar?start={start_index}&q={query.replace(' ', '+')}"

        print(f"Searching page {page + 1} for query: {query}")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                papers_list = soup.find_all("div", class_="gs_r")

                for paper in papers_list:
                    try:
                        title = paper.find("h3", class_="gs_rt").text.strip()
                        print(f"Title: {title}")

                        pdf_link = paper.find("div", class_="gs_or_ggsm")
                        print(f"AA {pdf_link}")
                        if pdf_link:
                            pdf_link_a = pdf_link.find("a")
                            if pdf_link_a:
                                pdf_url = pdf_link_a["href"]
                                print(f"PDF URL: {pdf_url}")
                                pdf_urls.append(pdf_url)
                            else:
                                print("PDF link not found")
                        else:
                            print("PDF link not found")
                    except Exception as e:
                        print(f"Error processing paper: {e}")
        except Exception as e:
            print(f"Error fetching page {page + 1}: {e}")
    return pdf_urls

def load_categories_from_csv(csv_file):
    categories = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            categories.append(row[0])
    return categories


if __name__ == "__main__":
    csv_file = "category.csv"
    categories = load_categories_from_csv(csv_file)
    print(categories)
    pages = int(input("Number of pages?: "))

    for category in categories:
        print(f"Searching papers for category: {category}")

        # Clear the pdf_urls list before starting to download papers for the next category
        pdf_urls.clear()

        pdf_urls = google_scholar_search(category, pages)
        download_pdfs(pdf_urls, category)
