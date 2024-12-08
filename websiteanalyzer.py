import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import validators
import json
import argparse


def analyze_website(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if not validators.url(url):
        return {"error": "Invalid URL"}

    report = {}
    try:
        response = requests.get(url, timeout=10)
        status_code = response.status_code
        report["Status Code"] = status_code
        if status_code != 200:
            report["Error"] = "Failed to fetch the website content"
            return report

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Load time and SSL check
        report["Load Time"] = round(response.elapsed.total_seconds(), 2)
        report["SSL Secured"] = "Yes" if url.startswith("https") else "No"

        # Title and Meta Description
        title = soup.title.string if soup.title else "Not Found"
        meta_description = soup.find("meta", attrs={"name": "description"})
        description_content = meta_description["content"] if meta_description else "Not Found"
        report["Title"] = title
        report["Meta Description"] = description_content

        # Mobile Responsiveness
        is_responsive = any(tag.get("name") == "viewport" for tag in soup.find_all("meta"))
        report["Mobile Responsive"] = "Yes" if is_responsive else "No"

        # Word Count
        word_count = len(soup.get_text().split())
        report["Word Count"] = word_count

        # Security Headers
        security_headers = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options"]
        headers = response.headers
        secure_headers_present = [header for header in security_headers if header in headers]
        report["Security Headers"] = ", ".join(secure_headers_present) if secure_headers_present else "None"

        # SEO Score
        keyword = "scale"  # Replace with your specific keyword
        seo_score = 0
        if keyword.lower() in title.lower():
            seo_score += 2
        if keyword.lower() in description_content.lower():
            seo_score += 2
        headers_text = soup.find_all(['h1', 'h2', 'h3'])
        if any(keyword.lower() in header.get_text().lower() for header in headers_text):
            seo_score += 2
        report["SEO Score"] = f"{seo_score}/6"

        # Images Analysis
        images = soup.find_all("img")
        missing_alts = [img for img in images if not img.get("alt")]
        report["Total Images"] = len(images)
        report["Missing Alt Attributes"] = len(missing_alts)

        # Broken Links
        links = [a['href'] for a in soup.find_all('a', href=True)]
        broken_links = []
        for link in links:
            if not link.startswith("http"):
                link = url + link
            try:
                link_response = requests.head(link, timeout=5)
                if link_response.status_code >= 400:
                    broken_links.append(link)
            except Exception:
                broken_links.append(link)
        report["Broken Links"] = len(broken_links)

        # Page Size
        page_size = int(headers.get("Content-Length", 0)) / 1024
        report["Page Size (KB)"] = round(page_size, 2)
        if page_size > 1024:
            report["Performance Warning"] = "Page size is too large and may affect load times."

        # Accessibility Checks
        forms = soup.find_all("form")
        inaccessible_forms = [form for form in forms if not form.get("aria-label")]
        report["Forms Without Accessibility Features"] = len(inaccessible_forms)

        # Review Score
        review_score = 0
        if report["SSL Secured"] == "Yes":
            review_score += 2
        if report["Mobile Responsive"] == "Yes":
            review_score += 2
        if len(secure_headers_present) >= 2:
            review_score += 2
        if word_count > 300:
            review_score += 2
        if report["Load Time"] < 3:
            review_score += 2
        report["Overall Score"] = f"{review_score}/10"

    except requests.exceptions.Timeout:
        report["Error"] = "The request timed out. The server might be down or unresponsive."
    except requests.exceptions.ConnectionError:
        report["Error"] = "Failed to establish a connection. Check the URL or your network."
    except Exception as e:
        report["Error"] = f"An unexpected error occurred: {str(e)}"

    return report


def display_report(report):
    if "error" in report:
        print(report["error"])
        return

    table = PrettyTable()
    table.field_names = ["Criteria", "Result"]

    for key, value in report.items():
        table.add_row([key, value])

    print(table)


def export_report(report, filename="report.json"):
    with open(filename, 'w') as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Website Analyzer")
    parser.add_argument("url", type=str, help="Website URL to analyze")
    parser.add_argument("--export", action="store_true", help="Export the report to a JSON file")
    args = parser.parse_args()

    website_report = analyze_website(args.url)
    display_report(website_report)

    if args.export:
        export_report(website_report)
