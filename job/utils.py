import random
from .models import Job, cache_job
from django.utils import timezone
from django.db.models import Q
import hashlib
from django.core.cache import cache


def generate_cache_key(
    search_query=None,
    organization_query=None,
    location=None,
    limits=None,
    job_title=None,
    job_address=None,
):
    key_string = f"{search_query}_{organization_query}_{location}_{str(limits)}_{job_title}_{job_address}"
    return key_string[:100]

def get_jobs(
    search_query=None,
    organization_query=None,
    location=None,
    limits=200,
    job_title=None,
    job_address=None,
    only_ids=False,
    disable_cache=False,
):
    cache_key = generate_cache_key(
        search_query, organization_query, location, limits, job_title, job_address
    )
    current_time = timezone.now()
    if disable_cache:
        jobs=None
    else:
        jobs = cache_job.get(cache_key)
    if not jobs:
        if search_query:
            jobs = (
                Job.objects.filter(
                    Q(title__icontains=search_query)
                    | Q(organization_name__icontains=search_query)
                    | Q(address_country__icontains=search_query)
                    | Q(address_locality__icontains=search_query)
                    | Q(address_region__icontains=search_query)
                    | Q(
                        address_complete_address=search_query,
                        validThrough__gt=current_time,
                    )
                )
                .only("id")[:limits]
                .iterator()
            )
            jobs = [job.id for job in jobs]

        elif search_query and organization_query:
            jobs = jobs = (
                Job.objects.filter(
                    Q(organization_name__icontains=organization_query)
                    | Q(title__icontains=search_query),
                    validThrough__gt=current_time,
                )
                .only("id")[:limits]
                .iterator()
            )
            jobs = [job.id for job in jobs]

        elif organization_query:
            jobs = (
                Job.objects.filter(
                    organization_name__icontains=organization_query,
                    validThrough__gt=current_time,
                )
                .only("id")[:limits]
                .iterator()
            )
            jobs = [job.id for job in jobs]

        elif location:
            jobs = (
                Job.objects.filter(
                    address_complete_address__icontains=location,
                    validThrough__gt=current_time,
                )
                .only("id")[:limits]
                .iterator()
            )
            jobs = [job.id for job in jobs]

        elif job_title and job_address:
            
            all_jobs  = Job.objects.filter(validThrough__gt=current_time).order_by("-created_at").only("id")[:limits].iterator()
            all_jobs = [job.id for job in all_jobs]
            all_jobs = Job.objects.filter(id__in=all_jobs)
            
            similar_jobs = []
            jobs = (
                all_jobs.filter(
                    title__icontains=job_title,
                    address_complete_address__icontains=job_address,
                )
                .only("id")[:10]
                .iterator()
            )
            similar_jobs.extend(job for job in jobs)
            if len(similar_jobs) < 10:
                title_words = job_title.split()  # Split title into words
                for word in title_words:
                    if len(similar_jobs) >= 10:
                        break
                    word_similar_jobs = (
                        (
                            all_jobs.filter(
                                Q(title__icontains=word)
                                | Q(address_complete_address=job_address)
                            )
                            .exclude(pk__in=[j.id for j in similar_jobs])
                        )
                        .only("id")[:10]
                        .iterator()
                    )
                    if len(similar_jobs)>=10:
                        break
                    similar_jobs.extend(word_similar_jobs)

                jobs = [job.id for job in similar_jobs]
            else:
                jobs = [job.id for job in similar_jobs]
        else:
            jobs =  Job.objects.filter(validThrough__gt=current_time).order_by("-created_at").only("id")[:limits].iterator()
            jobs = [job.id for job in jobs]

        if only_ids is True:
            return jobs
        else:
            if jobs:
                cache_job.set(cache_key=cache_key, jobs=jobs)
        
        return Job.objects.filter(id__in=jobs).order_by("-created_at")
    else:
        return Job.objects.filter(id__in=jobs).order_by("-created_at")


def generate_keywords(job, lists=False):
    title_words = job.title.split() if job.title else []
    address_words = job.address_complete_address.split()
    organization_words = job.organization_name.split()

    # Adding "jobs" as a keyword
    all_words = title_words + address_words + organization_words + ["jobs"]
    if not lists:
        keywords = " ".join(all_words)
    else:
        keywords = all_words

    return keywords


def get_similar_jobs(job):
    return get_jobs(
        job_title=job.title, job_address=job.address_complete_address,only_ids=True,disable_cache=True)
