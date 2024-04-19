import csv
import time
import requests
import os
from bs4 import BeautifulSoup

pdf_urls = []

def download_pdfs(pdf_urls, category):
    category_dir = os.path.join("arxiv", category)
    os.makedirs(category_dir, exist_ok=True)  # Create directory if it doesn't exist
    for idx, pdf_url in enumerate(pdf_urls):
        try:
            response = requests.get(pdf_url, stream=True)
            if response.status_code == 200:
                with open(os.path.join(category_dir, f"Arxiv_{category}_{idx+1}.pdf"), "wb") as f:  # Save in category directory
                    f.write(response.content)
                print(f"Downloaded paper {idx + 1} for category {category}")
            else:
                print(f"Failed to download paper {idx + 1} for category {category}: Status code {response.status_code}")
        except Exception as e:
            print(f"Error downloading paper {idx + 1} for category {category}: {e}")

def arxiv_search(query, max_pages):
    for page in range(max_pages):
        start_index = page * 50
        url = f"https://arxiv.org/search/?query={query.replace(' ', '+')}&searchtype=all&abstracts=show&order=-announced_date_first&size=50&start={start_index}"

        print(f"Searching page {page + 1} for query: {query}")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                papers_list = soup.find_all("li", class_="arxiv-result")

                for paper in papers_list:
                    try:
                        title = paper.find("p", class_="title").text.strip()
                        print(f"Title: {title}")

                        pdf_link = paper.find("a", text="pdf")
                        if pdf_link:
                            pdf_url = pdf_link["href"]
                            print(f"PDF URL: {pdf_url}")
                            pdf_urls.append(pdf_url)
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
        pdf_urls.clear()


        pdf_urls = arxiv_search(category, pages)
        download_pdfs(pdf_urls, category)
