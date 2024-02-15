#!/usr/bin/env python
"""
Exit with 0 if GHA job should be run because:
 - it was not run yet
 - it failed in previous run attempt
Exit with 1 if job should not be run because
 - it succeeded in previous run attempt
"""
import os
import sys
import json
import logging
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def url_get_json(url):
    with urllib.request.urlopen(url) as response:
        content = response.read()
        return json.loads(content)


def output_retry_job_names(retry_job_names):
    logger.info("retry_job_names=%s", retry_job_names)
    for name in retry_job_names:
        print(f"    {name}")


def main():
    # repo = "https://github.com/justinc1/gha-experiment"
    # repo_api = " https://api.github.com/repos/justinc1/gha-experiment"
    # run_id = "7871225452"
    repo_api = f"{os.environ['GITHUB_API_URL']}/repos/{os.environ['GITHUB_REPOSITORY']}"
    run_id = os.environ["GITHUB_RUN_ID"]
    job_name = os.environ["X_GITHUB_JOB_NAME"]

    run_data = url_get_json(f"{repo_api}/actions/runs/{run_id}")
    # print(f"run_data={json.dumps(run_data, indent=4)}")
    run_attempt = run_data['run_attempt']
    logger.info("Latest/current run_attempt=%s", run_attempt)
    if run_attempt == 1:
        output_retry_job_names([])
        logger.info("RUN, job_name=%s, run_attempt==1", job_name)
        return

    previous_attempt_url = run_data['previous_attempt_url']
    # print(f"previous_attempt_url={run_data['previous_attempt_url']}")
    # previous_attempt_data = requests.get(previous_attempt_url).json()
    previous_attempt_jobs_url = f"{previous_attempt_url}/jobs"
    logger.info("previous_attempt_jobs_url=%s", previous_attempt_jobs_url)

    _jobs_data = url_get_json(previous_attempt_jobs_url)
    previous_jobs = _jobs_data["jobs"]
    logger.info("previous_jobs count=%d", len(previous_jobs))
    for job in previous_jobs:
        logger.info(
            "job id=%s status=%s conclusion=%s name=%s",
            job["id"], job["status"], job["conclusion"], job["name"]
        )

    # Decide which jobs should NOT be re-run.
    # https://docs.github.com/en/actions/learn-github-actions/contexts#steps-context
    # conclusion == success, failure, cancelled, or skipped.
    retry_needed_jobs = [
        job
        for job in previous_jobs
        if job["conclusion"] in ["failure", "cancelled"]
    ]
    retry_job_names = [
        job["name"]
        for job in retry_needed_jobs
    ]
    output_retry_job_names(retry_job_names)

    if job_name in retry_job_names:
        logger.info("RETRY, job_name='%s' in retry_job_names", job_name)
        return
    else:
        logger.info("SKIP, job_name='%s' not in retry_job_names", job_name)
        sys.exit(1)


if __name__ == "__main__":
    main()
