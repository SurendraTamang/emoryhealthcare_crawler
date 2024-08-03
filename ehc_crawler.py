import requests
import re
import json
import logging

logging.basicConfig(level=logging.INFO)

def grab_jobs_list():
    """
    Fetches a list of job postings from the Emory non-clinical job search page.

    This function iterates through the paginated job search results, fetching job details
    from each page until no new job IDs are found. The job details are extracted from the
    JavaScript variable `jobImpressions` present in the page's HTML.

    Returns:
        list: A list of job details dictionaries.
    """

    total_jobs = list()
    i = 0
    unique_ids = set()
    
    while True:
        logging.info(f"Fetching page {i}")
        url = f'https://non-clinical-emory.icims.com/jobs/search?pr={i}&searchRelation=keyword_all&in_iframe=1&mobile=false&width=1240&height=500&bga=true&needsRedirect=false&jan1offset=0&jun1offset=3450'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            break
        
        previous_len = len(unique_ids)
        job_details = re.findall("jobImpressions = (.*);", response.text)
        
        if job_details:
            try:
                job_details_list = json.loads(job_details[0])
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                break
            
            total_jobs.extend(job_details_list)
            unique_ids.update(x.get('idRaw') for x in total_jobs)
        
        if len(unique_ids) == previous_len:
            break
        else:
            i += 1
    
    return total_jobs

def main():
    jobs_list = grab_jobs_list()
    with open('job_details.json', 'w') as jd:
        json.dump(jobs_list, jd, indent=4)

if __name__ == '__main__':
    main()