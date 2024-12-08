import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import validators

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

        report["Load Time"] = round(response.elapsed.total_seconds(), 2)
        report["SSL Secured"] = "Yes" if url.startswith("https") else "No"

        title = soup.title.string if soup.title else "Not Found"
        meta_description = soup.find("meta", attrs={"name": "description"})
        description_content = meta_description["content"] if meta_description else "Not Found"
        report["Title"] = title
        report["Meta Description"] = description_content

        is_responsive = any(tag.get("name") == "viewport" for tag in soup.find_all("meta"))
        report["Mobile Responsive"] = "Yes" if is_responsive else "No"

        word_count = len(soup.get_text().split())
        report["Word Count"] = word_count

        security_headers = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options"]
        headers = response.headers
        secure_headers_present = [header for header in security_headers if header in headers]
        report["Security Headers"] = ", ".join(secure_headers_present) if secure_headers_present else "None"

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

    except Exception as e:
        report["Error"] = f"An error occurred: {str(e)}"

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

if __name__ == "__main__":
    url = input("Enter the website URL: ")
    website_report = analyze_website(url)
    display_report(website_report)
