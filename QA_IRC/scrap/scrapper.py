import os
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://irc.bloombergtax.com"
OUTPUT_DIR = "sections"
LOG_FILE_UNEXTRACTED = "unextracts_links_log.txt"
LOG_FILE_EXTRACTED = "extracts_links_log.txt"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def log_link(log_file, link):
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(link + "\n")

def extract_links(url, keywords):
    print(f"Extracting links from: {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"Failed to access {url}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    filtered_links = []
    
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(keyword.lower() in href.lower() for keyword in keywords):  
            full_url = BASE_URL + href
            filtered_links.append(full_url)
    
    print(f"Found {len(filtered_links)} links matching criteria in {url}")
    return filtered_links

def extract_section_text(section_url):
    print(f"Extracting text from: {section_url}")
    response = requests.get(section_url, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code != 200:
        print(f"Failed to retrieve {section_url}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    title_tag = soup.find("h1", class_="sub_title")
    title = title_tag.text.strip() if title_tag else "Unknown Title"
    
    extracted_text = []
    for section in soup.find_all("div", class_="segment-level"):
        if section.find_parent("div", class_="segment-level") is None:
            extracted_text.append(section.text.strip())
    
    if extracted_text:
        print(f"Successfully extracted text from: {section_url}")
    else:
        print(f"No text extracted from: {section_url}")
    
    return title, "\n".join(extracted_text)

subtitle_links = extract_links(BASE_URL, ["subtitle"])
chapter_links = [link for subtitle_url in subtitle_links for link in extract_links(subtitle_url, ["chapter"])]
subchapter_links = [link for chapter_url in chapter_links for link in extract_links(chapter_url, ["subchapter"])]

section_links = []
for subchapter_url in subchapter_links:
    print(f"Extracting parts & sections from: {subchapter_url}")
    part_section_links = extract_links(subchapter_url, ["part", "section"])
    section_links.extend([link for link in part_section_links if "section" in link.lower()])
    for part_url in part_section_links:
        if "part" in part_url.lower():
            print(f"Extracting sections from: {part_url}")
            section_links.extend(extract_links(part_url, ["section"]))
    time.sleep(1)

for section_url in section_links:
    print(f"Downloading: {section_url}")
    title, text = extract_section_text(section_url)
    if title and text.strip():
        filename = title.replace(" ", "_").replace(".", "").replace(",", "") + ".txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"{title}\n\n{text}")
        log_link(LOG_FILE_EXTRACTED, section_url)
    else:
        log_link(LOG_FILE_UNEXTRACTED, section_url)

print(f"\nExtraction complete. {len(section_links)} sections processed.")
