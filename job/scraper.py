import pycountry
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
from django.conf import settings
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from datetime import datetime
from django.conf import settings
import html, string
from .utils import get_similar_jobs, generate_cache_key
import os


def redirect_fix(html):
    pattern = re.compile(r'href="([^"]+)"')

    def replace_url(match):
        original_url = match.group(1)
        new_url = f"/redirect?url={original_url}"
        return f'href="{new_url}"'

    modified_html = pattern.sub(replace_url, html)

    return modified_html


from oauth2client.service_account import ServiceAccountCredentials
import httplib2


def Send_to_Indexing(urls, API_Path="key.json"):

    SCOPES = ["https://www.googleapis.com/auth/indexing"]
    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

    JSON_KEY_FILE = API_Path
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        JSON_KEY_FILE, scopes=SCOPES
    )
    http = credentials.authorize(httplib2.Http())

    if type(urls) == list:
        for siteURL in urls:
            try:
                requests.get(siteURL)
            except:
                pass
            requestType = "URL_UPDATED"
            content = str({"url": siteURL, "type": requestType})

            response, content = http.request(ENDPOINT, method="POST", body=content)
            output = response["status"]
    else:
        try:
            requests.get(urls)
        except:
            pass
        requestType = "URL_UPDATED"
        content = str({"url": urls, "type": requestType})

        response, content = http.request(ENDPOINT, method="POST", body=content)
        output = response["status"]


def insert_jobs_from_list(data_list, current_domain, logo_change=False):
    directory = os.path.join(os.getcwd(), "static/assets/images/logo")
    counts = 0

    for data in data_list:
        counts += 1
        try:
            try:
                del data["url"]
            except:
                pass
            title = data.get("title").replace("/", " - ")
            organization_data = data["hiringOrganization"]
            if not organization_data.get("logo", None):
                organization_data["logo"] = ""
            organization_name = (
                organization_data.get("name").replace("/", "-").replace("#", "-")
            )

            os.makedirs(directory, exist_ok=True)
            the_filename = (
                organization_data.get("logo").split("/")[-1].replace("---", "-")
            )
            extension = "." + the_filename.split(".")[-1]
            path = organization_name.lower()

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
            streetAddress = address_data.get("streetAddress", None)

            if not address_data:
                try:
                    country = data["jobLocation"]["name"]
                except:
                    pass

            if not country and not region and not locality:
                country = ""
            if not locality and not region and streetAddress:
                locality = streetAddress

            if not locality and not region:
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
            try:
                if len(BeautifulSoup(description, "html.parser").find_all()) == 0:
                    description = (
                        '<pre style="font-family: inherit;">' + description + "</pre>"
                    )
            except:
                description = (
                    '<pre style="font-family: inherit;">' + description + "</pre>"
                )
            validThrough = data.get("validThrough")
            apply_url = data.get("apply_url", None)
            if not apply_url or apply_url == "":
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
                    address_region=region,
                    address_locality=locality,
                    address_country=country,
                    salary_currency=currency,
                    salary_minValue=minValue,
                    salary_maxValue=maxValue,
                    salary_unitText=unitText,
                )
                job.apply_url = apply_url
                job.og_job_id = job_id
                job.schema = data
                job.validThrough = validThrough
                job.save()
                similar = get_similar_jobs(job)
                job.related_jobs = similar
                job.save()
            elif title and validThrough:
                job, created = Job.objects.get_or_create(
                    title=title,
                    description=description,
                    organization_name=organization_name,
                    organization_website=or_website,
                    address_region=region,
                    address_locality=locality,
                    address_country=country,
                    salary_currency=currency,
                    salary_minValue=minValue,
                    salary_maxValue=maxValue,
                    salary_unitText=unitText,
                )
                job.apply_url = apply_url
                job.og_job_id = job_id
                job.schema = data
                job.validThrough = validThrough
                job.save()
                similar = get_similar_jobs(job)
                job.related_jobs = similar
                job.save()

        except Exception as e:
            import traceback

            traceback.print_exc()
