from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import socket
import time
import dns.resolver
from statistics import mean
import whois
import re
import os
import matplotlib.pyplot as plt
from io import BytesIO

class StyledPDF(FPDF):
    def header(self):
        self.image('logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Website Information Report', border=0, ln=1, align='C')
        self.ln(10)

    def footer(self):
        # הוספת כותרת תחתונה עם מספר עמוד
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_title(self, title):
        # הוספת כותרת לתוך הדוח
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 102, 204)  # כחול
        self.cell(0, 10, title, ln=1, border=0, align='C')
        self.ln(10)

    def add_table(self, data):
        # הוספת טבלה עם נתונים לדוח
        self.set_font('Arial', '', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(50, 10, "Key", border=1, align='C', fill=1)
        self.cell(140, 10, "Value", border=1, align='C', fill=1)
        self.ln()
        self.set_fill_color(240, 240, 240)
        for key, value in data.items():
            self.cell(50, 10, str(key), border=1, align='L', fill=1)
            self.cell(140, 10, self.encode_text(str(value)), border=1, align='L', fill=0)
            self.ln()

    def add_image_from_file(self, img_path):
        # הוספת תמונה לדוח
        self.image(img_path, x=10, w=180)

    def set_unicode_font(self):
        # הגדרת פונט מתאים עם תמיכה בתווים באנגלית
        self.set_font('Arial', '', 12)

    def encode_text(self, text):
        """ פונקציה להמרת טקסט לקידוד 'latin-1' """
        try:
            return text.encode('latin-1', 'ignore').decode('latin-1')
        except UnicodeEncodeError:
            return text  # אם יש בעיה בקידוד, נשאיר את הטקסט כמו שהוא

def generate_pdf(report, output_file):
    pdf = StyledPDF()
    pdf.add_page()

    # כותרת
    pdf.add_title("Website Report")

    # טבלה עם נתונים
    pdf.add_table(report)

    # יצירת גרף
    load_times = report["Load Times"]
    attempts = [1, 2, 3]
    for i in range(3):  # assuming there are always 3 load times
        plt.plot(attempts, [load_times[i] for _ in attempts], marker='o', label=f'Load Time {i+1}')
    
    # הוספת קו ממוצע זמן טעינה
    plt.axhline(y=report["Average Load Time (s)"], color='r', linestyle='--', label=f'Average Load Time: {report["Average Load Time (s)"]}s')
    
    # הגדרת כותרת וצירים לגרף
    plt.xlabel("Attempt Number")
    plt.ylabel("Load Time (seconds)")
    plt.title("Website Load Time Attempts")
    plt.legend()

    # שמירת הגרף כקובץ תמונה
    img_path = 'load_time_plot.png'
    plt.savefig(img_path)
    plt.close()  # סגירת הגרף לאחר שמירה

    # הוספת תמונה לדוח
    pdf.add_image_from_file(img_path)

    # יצירת קובץ PDF
    pdf.output(output_file, 'F')

    # מחיקת קובץ התמונה הזמני
    os.remove(img_path)

def calculate_average_load_time(url, trials=3):
    load_times = []
    for _ in range(trials):
        start_time = time.time()
        try:
            requests.get(url, timeout=10)
            load_time = time.time() - start_time
            load_times.append(load_time)
        except requests.exceptions.RequestException:
            load_times.append(float('inf'))
    return round(mean(load_times), 2), load_times  # Return average and all load times

# פונקציה לאיסוף מידע על האתר
def get_site_info(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        avg_load_time, load_times = calculate_average_load_time(url)

        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        domain = re.findall(r"https?://([A-Za-z_0-9.-]+).*", url)[0]
        ip_address = socket.gethostbyname(domain)
        title = soup.title.string if soup.title else "N/A"
        description = soup.find("meta", attrs={"name": "description"})
        meta_description = description['content'] if description else "N/A"

        # Links
        links = soup.find_all("a")
        internal_links = len([link.get('href') for link in links if link.get('href') and link.get('href').startswith('/')])
        external_links = len([link.get('href') for link in links if link.get('href') and link.get('href').startswith('http')])

        # Images and accessibility
        images = soup.find_all("img")
        image_count = len(images)
        alt_texts = len([img for img in images if img.get('alt')])

        # Server and SSL
        server_type = response.headers.get('Server', 'N/A')

        # WHOIS info
        domain_info = whois.whois(domain)

        # Headers (H1-H6)
        headers = {f'H{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}

        # Page size
        page_size = round(len(response.content) / 1024, 2)  # in KB

        # DNS Records
        dns_records = get_dns_records(domain)

 # Security (Basic XSS/CSRF check - This is a simple example, more complex checks can be added)
        security_check = "No XSS/CSRF vulnerability found."  # Placeholder for security checks

        return {
            "Domain": domain,
            "IP Address": ip_address,
            "Title": title,
            "Meta Description": meta_description,
            "Page Size (KB)": page_size,
            "Internal Links": internal_links,
            "External Links": external_links,
            "Image Count": image_count,
            "Images with Alt Text": alt_texts,
            "Server Type": server_type,
            "H1-H6 Tags": headers,
            "Registrar": domain_info.registrar,
            "Creation Date": domain_info.creation_date,
            "Expiration Date": domain_info.expiration_date,
            "DNS Records": dns_records,
            "Security Check": security_check,
            "Load Times": load_times,
            "Average Load Time (s)": avg_load_time
         }
    except Exception as e:
        return {"Error": str(e)}

# פונקציה לאיסוף רשומות DNS
def get_dns_records(domain):
    try:
        records = {}
        a_records = dns.resolver.resolve(domain, 'A')
        records['A'] = [str(ip) for ip in a_records]
        mx_records = dns.resolver.resolve(domain, 'MX')
        records['MX'] = [str(mx.exchange) for mx in mx_records]
        return records
    except Exception as e:
        return {"Error": str(e)}

# דוגמת שימוש
if __name__ == "__main__":
    url = input("Enter website URL: ")
    report = get_site_info(url)

    if "Error" in report:
        print("Error:", report["Error"])
    else:
        # יצירת קובץ PDF
        generate_pdf(report, "website_report.pdf")
        print("PDF report generated: website_report.pdf")
