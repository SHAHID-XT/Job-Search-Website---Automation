import requests
from bs4 import BeautifulSoup
import json
import csv
import re
from datetime import datetime
import time, random
from datetime import datetime, timedelta
import threading
from job.models import *
from .helper import *
from django.conf import settings
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from datetime import datetime
from django.conf import settings
import html

try:
    import pycountry
except:
    os.system("pip install pycountry")
    import pycountry


def print(*args, **kwargs):
    pass


def redirect_fix(html):
    pattern = re.compile(r'href="([^"]+)"')

    def replace_url(match):
        original_url = match.group(1)
        new_url = f"/redirect?url={original_url}"
        return f'href="{new_url}"'

    modified_html = pattern.sub(replace_url, html)

    return modified_html


class indevjobs:
    storage_json = "history3.json"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8,ur;q=0.7",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "Referer": "http://localhost:8888/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    def __init__(self) -> None:
        self.history = self.read_from_json(self.storage_json)

    def write_to_json(self, data, json_file):
        try:
            with open(json_file, "w", encoding="utf-8") as json_file:
                json.dump(
                    data,
                    json_file,
                )  # Write data to JSON file with indentation for readability
            return True
        except Exception as e:
            print(e)
            return False

    def read_from_json(self, json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)  # Read data from JSON file
            return data
        except:
            return []

    def scrape_urls(self, max_pages=1):
        urls = []
        for page_num in range(1, max_pages + 1):
            try:
                r = requests.get(
                    f"https://indevjobs.org/?page={page_num}", headers=self.headers
                )
                page = BeautifulSoup(r.text, "html.parser")
                for url in page.find_all(class_="job-box"):

                    u = url.parent.get("href")
                    if u in self.history:
                        continue
                    self.history.append(u)
                    urls.append(u)
                    time.sleep(random.randint(5, 10))

            except:
                pass
        self.write_to_json(self.history, self.storage_json)
        return urls

    def scrape_schema(self, url):
        try:
            r = requests.get(url, headers=self.headers)
            job_page = BeautifulSoup(r.text, "html.parser")
            job_img = job_page.find(class_="job-img").find("img").get("src")
            job_info = None
            try:
                job_info = json.loads(
                    job_page.find("script", type="application/ld+json").text
                )
                job_info["hiringOrganization"]["logo"] = job_img
                job_info["description"] = html.unescape(job_info["description"])
                valid_through_date = datetime.strptime(
                    job_info["validThrough"], "%d-%m-%Y"
                ).strftime("%Y-%m-%d 23:59:59")
                job_info["validThrough"] = valid_through_date

                soup = BeautifulSoup(job_info["description"], "html.parser")
                all_p = soup.find_all("p")
                try:
                    if all_p:
                        last_p = all_p[-1]
                        apply = last_p.find("a").get("href")
                        job_info["apply_url"] = apply
                except:
                    pass
                try:
                    if all_p:
                        last_p = all_p[-2]
                        apply = last_p.find("a").get("href")
                        job_info["apply_url"] = apply
                except:
                    pass

            except Exception as e:
                print(e)
                job_info = None
            return job_info
        except Exception as e:
            print(e)
            pass

        return job_info

    def scrape(self, max_pages=1):
        data = []
        urls = self.scrape_urls(max_pages)
        for url in urls:
            d = self.scrape_schema(url)
            if d:
                data.append(d)
        return data


class Untalent:
    api_key = "1d6530c224a833855291bf4b7ffc0196"
    api_url = "http://api.scraperapi.com"
    data = []
    storage_json = "history2.json"

    def __init__(self):
        self.base_url = "https://untalent.org/jobs/"
        self.history = self.read_from_json(self.storage_json)
        self.counter = self.read_from_json("templates\counter.json")

    def find_jobs_links(self, max_pages=4):
        jobs = []
        try:
            for page in range(1, max_pages + 1):
                try:
                    url = self.base_url + f"?page={page}"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, "html.parser")
                    job_cards = soup.find_all(class_="job card")
                    if not job_cards:
                        job_cards = BeautifulSoup(
                            self.backup_fetcher(url).text, "html.parser"
                        ).find_all(class_="job card")
                    job = [
                        f.find(class_="content").find("h4").find("a").get("href")
                        for f in job_cards
                    ]
                    filter_job = []
                    for link in job:
                        if not link in self.history:
                            filter_job.append(link)
                            self.history.append(link)
                    jobs.extend(filter_job)
                    self.write_to_json(list(set(self.history)), self.storage_json)
                except Exception as e:
                    pass
            return jobs

        except Exception as e:
            return []

    def get_job_details(self, job_url):

        if job_url not in self.history:
            self.history.append(job_url)

        print(f"Getting job details from : %s" % job_url)
        try:

            r = requests.get(job_url)
            job_page = BeautifulSoup(r.text, "html.parser")
            try:
                job_info = json.loads(
                    job_page.find("script", type="application/ld+json").text
                )
            except:
                job_info = None

            if not job_info:
                r = self.backup_fetcher(job_url)
                job_page = BeautifulSoup(r.text, "html.parser")
                job_info = json.loads(
                    job_page.find("script", type="application/ld+json").text
                )

            description_html = str(
                job_page.find(class_="card partner").find_next_sibling()
            )
            job_info["description"] = description_html
            apply_link = self.get_direct_apply_link(job_url)

            if apply_link:
                job_info["apply_url"] = apply_link
                return job_info
            return None

        except Exception as e:
            return {}

    def write_to_json(self, data, json_file):
        try:
            with open(json_file, "w", encoding="utf-8") as json_file:
                json.dump(
                    data, json_file, indent=4
                )  # Write data to JSON file with indentation for readability
            return True
        except:
            return False

    def read_from_json(self, json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)  # Read data from JSON file
            return data
        except:
            return []

    def iterate_links(self, links):
        self.data = []
        for link in links:
            print(link)
            try:
                d = self.get_job_details(link)
                if d:
                    self.data.append(d)
                    time.sleep(random.randint(3, 9))

            except KeyboardInterrupt as e:
                return self.data
        return self.data

    def backup_fetcher(self, url):
        payload = {"api_key": self.api_key, "url": url, "render": "true"}
        response = requests.get(self.api_url, params=payload)
        return response

    def get_direct_apply_link(self, url):
        # Headers
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Te": "trailers",
        }

        # Cookies
        cookies = {
            "PHPSESSID": "40tjk03m3c88847ph5oafc1c90a4nl0i",
            "REMEMBERME": "UHJveGllc1xfX0NHX19cQXBwXEVudGl0eVxVc2VyOmVIUnpZbTlzZEdWQVoyMWhhV3d1WTI5dDoxNzQ3NjQxOTY3OmZkNTFhMzY4NjRmNGU0OWIxY2IzNzIyZjIwNjExNWE3NTA3NmFhOTU3ZmRjZTg5YTk2NzEzZWVlMjE2YTBkY2Q%3D",
        }

        # Make the GET request
        response = requests.get(url + "/apply", headers=headers, cookies=cookies)

        if not "untalent.org" in str(response.url):
            return response.url
        else:
            return None


class unjobnet:

    json_headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en,hi;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
    }
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8,ur;q=0.7",
        "priority": "u=0, i",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    def __init__(self) -> None:
        self.history = self.read_json("history.json")

    def _get_page_posts(self, page_num):
        try:
            res = requests.get(
                f"https://www.unjobnet.org/jobs?&page={page_num}",
                headers=self.json_headers,
            )
            jobs = res.json()["jobs"]
            next_page = res.json()["pager"]["next"]
            return jobs, next_page
        except Exception as e:
            return [None, None]

    def _get_page_details(self, id):
        if id in self.history:
            print("id is in history")
            return None
        else:
            self.history.append(id)

        try:
            page = requests.get(
                f"https://www.unjobnet.org/jobs/detail/{id}", headers=self.headers
            ).text
            soup = BeautifulSoup(page, "html.parser")
            schema = json.loads(soup.find("script", type="application/ld+json").text)
            schema = self._update_schema(
                schema, property_name="talenttrackers.online", website_url="xt.com"
            )
            linkk = self.get_apply_link(id)
            schema["apply_url"] = linkk
            return schema
        except Exception as e:
            import traceback

            traceback.print_exc()
            return None

    def random_sleep(self):
        time.sleep(random.randint(3, 9))

    def _scrape_job(self, max_pages=1):
        data = []
        for page in range(1, max_pages + 1):
            try:
                page_json, next_page = self._get_page_posts(page)
                if page_json:
                    for u in page_json:
                        d = self._get_page_details(u["JobID"])
                        if d:
                            data.append(d)
                        time.sleep(random.randint(2, 4))
                self.scrape_data = data
                # self.write_list_to_json(data)
            except Exception as e:
                import traceback

                traceback.print_exc()
                pass

        self.write_list_to_json(list(set(self.history)), "history.json")

        return data

    def read_from_csv(self, csv_file):
        data = []
        try:
            with open(csv_file, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(dict(row))
        except:
            return []
        return data

    def read_json(self, filename="automatic/jobs.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            print(f"Data has been read from {filename}")
            return data
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def write_list_to_json(self, data, filename="automatic/jobs.json"):
        """
        Writes a list to a JSON file.

        Parameters:
        data (list): The list to write to the JSON file.
        filename (str): The name of the file to write the JSON data to.
        """
        old_data = self.read_json(filename)

        if old_data:
            data.extend(old_data)
        try:
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
            print(f"Data has been written to {filename}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _update_schema(self, data, property_name, website_url="unjobnet.org"):
        try:
            data["identifier"]["name"] = property_name
            data["hiringOrganization"]["logo"] = data["hiringOrganization"][
                "logo"
            ].replace("unjobnet.org", website_url)
            data["hiringOrganization"]["sameAs"] = data["hiringOrganization"][
                "sameAs"
            ].replace("unjobnet.org", website_url)
            try:
                formatted_date = datetime.strptime(
                    re.search(r"Close on (\d+ \w+ \d{4})", data["validThrough"]).group(
                        1
                    ),
                    "%d %b %Y",
                )
                data["validThrough"] = str(formatted_date)
            except Exception as e:
                today = datetime.now()
                # Add 30 days to today's date
                future_date = today + timedelta(days=30)
                data["validThrough"] = str(future_date)
            return data
        except Exception as e:
            return data

    def get_apply_link(self, jobid):
        try:
            response = requests.get(
                f"https://www.unjobnet.org/apply/{jobid}",
                allow_redirects=True,
                headers=self.headers,
            )
            if response.status_code == 200:
                print(response.url)
                final_url = response.url
                return final_url
            else:
                print(response.text)
        except Exception as e:
            return None


import string


def insert_jobs_from_list(data_list, current_domain, logo_change=False):
    print(current_domain)
    directory = os.path.join(os.getcwd(), "static/assets/images/logo")
    counts = 0
    print(len(data_list))
    for data in data_list:
        print(data)
        try:
            try:
                del data["url"]
            except:
                pass
            title = data.get("title")
            organization_data = data["hiringOrganization"]
            if not organization_data.get("logo", None):
                organization_data["logo"] = ""
            organization_name = (
                organization_data.get("name").replace("/", "-").replace("#", "-")
            )
            characters_to_replace = [
                "/",
                "#",
                "?",
                "&",
                "=",
                "+",
                "%",
                "\\",
                "|",
                "{",
                "}",
                "[",
                "]",
                "^",
                "`",
                "<",
                ">",
                '"',
                "'",
                ":",
                ";",
                "@",
                "!",
                "$",
                "(",
                ")",
                "*",
                ",",
                ".",
                "~",
            ]
            for char in characters_to_replace:
                organization_name = organization_name.replace(char, "-")
                title = title.replace(char, "-")

            os.makedirs(directory, exist_ok=True)
            the_filename = (
                organization_data.get("logo").split("/")[-1].replace("---", "-")
            )
            extension = "." + the_filename.split(".")[-1]
            path = (
                organization_name.lower()
                .replace(" ", "-")
                .replace("_", "-")
                .replace("/", "-")
                .replace("\/", "-")
                + extension
            )
            filename = os.path.join(
                directory,
                path,
            )
            backup_filename = None
            characters = string.ascii_letters + string.digits
            random_string = None

            while True:
                random_string = "".join(random.choice(characters) for _ in range(15))
                backup_filename = os.path.join(directory, random_string + extension)
                if os.path.exists(backup_filename):
                    continue
                break

            or_website = current_domain + "/organization/" + "" + organization_name

            urldownload = f"https://www.unjobnet.org/assets/images/organization/logo/{the_filename}"
            if logo_change:
                urldownload = organization_data.get("logo")
            is_backup_trigger = False
            # print(filename)
            if not os.path.exists(filename) and organization_data.get("logo"):
                response = requests.get(urldownload)
                response.raise_for_status()
                try:
                    with open(filename, "wb") as file:
                        file.write(response.content)
                except:
                    is_backup_trigger = True
                    with open(backup_filename, "wb") as file:
                        file.write(response.content)
            logo = current_domain + "/public/assets/images/logo/" + path
            if is_backup_trigger:
                logo = (
                    current_domain
                    + "/public/assets/images/logo/"
                    + random_string
                    + extension
                )
            if not organization_data.get("logo"):
                logo = False
            try:
                address_data = data["jobLocation"][0]["address"]
            except Exception as a:
                try:
                    address_data = data["jobLocation"]["address"]
                except:
                    address_data = {}

            locality = address_data.get("addressLocality", None)
            region = address_data.get("addressRegion", None)
            country = address_data.get("addressCountry", None)

            if not address_data:
                try:
                    country = data["jobLocation"]["name"]
                except:
                    pass

            if not country and not region and not locality:
                country = "Unknown"

            if country == "Unknown":
                continue

            try:
                if len(country) == 2:
                    country = pycountry.countries.get(alpha_2=country.upper()).name
            except:
                pass

            data["hiringOrganization"]["logo"] = logo
            data["hiringOrganization"]["sameAs"] = or_website

            try:
                salary_data = data["baseSalary"]["value"]
            except:
                salary_data = {}

            try:

                currency = data["baseSalary"]["currency"]
            except:
                currency = "USD"

            minValue = salary_data.get("minValue", 0.00)
            maxValue = salary_data.get("maxValue", 0.00)
            unitText = salary_data.get("unitText", "YEAR")

            description = redirect_fix(data.get("description"))
            pattern = r" Job Posted by .*? "
            description = re.sub(pattern, "", description)
            description = html.unescape(description)
            validThrough = data.get("validThrough")
            apply_url = data.get("apply_url")
            if not apply_url:
                continue
            try:
                job_id = data.get("identifier")["value"]
            except:
                job_id = 0

            if title and validThrough and logo:
                job, created = Job.objects.get_or_create(
                    title=title,
                    description=description,
                    organization_name=organization_name,
                    organization_logo=logo,
                    organization_website=or_website,
                    apply_url=apply_url,
                    address_region=region,
                    address_locality=locality,
                    address_country=country,
                    salary_currency=currency,
                    salary_minValue=minValue,
                    salary_maxValue=maxValue,
                    salary_unitText=unitText,
                )

                job.og_job_id = job_id
                job.schema = data
                job.validThrough = validThrough
                job.save()
            elif title and validThrough:
                job, created = Job.objects.get_or_create(
                    title=title,
                    description=description,
                    organization_name=organization_name,
                    organization_website=or_website,
                    apply_url=apply_url,
                    address_region=region,
                    address_locality=locality,
                    address_country=country,
                    salary_currency=currency,
                    salary_minValue=minValue,
                    salary_maxValue=maxValue,
                    salary_unitText=unitText,
                )

                job.og_job_id = job_id
                job.schema = data
                job.validThrough = validThrough
                job.save()
        except Exception as e:
            print(data)
            import traceback

            traceback.print_exc()


lock = threading.Lock()


def Run_populate_job():
    lock.acquire()
    sleep1 = random.randint(40, 100)
    sleep2 = random.randint(50, 200)
    time.sleep(sleep1)

    while True:
        time.sleep(60 * 60 * 24)
        if read_json()["is_running"]:
            print("already running...")
            break

        write_json({"is_running": True})

        print("Running Populate")

        domain = settings.WEBSITE_DOMAIN
        try:
            print("running Populate")
            j = indevjobs()
            data = j.scrape(15)
            insert_jobs_from_list(data, domain, True)
        except:
            pass

        try:
            j = unjobnet()
            data = j._scrape_job(12)
            print("geeting data")
            print(len(data))
            insert_jobs_from_list(data, domain)
        except Exception as e:
            print(e)
        except KeyboardInterrupt as e:
            break
        try:
            k = Untalent()
            links = k.find_jobs_links(13)
            data = k.iterate_links(links)
            insert_jobs_from_list(data, domain, True)
        except Exception as e:
            print(e)

        os.system("sudo service gunicorn restart")

    lock.release()


def start_population_thread():
    if not settings.DOMAIN == "127.0.0.1":
        thread = threading.Thread(target=Run_populate_job)
        thread.start()
