#!/usr/bin/env python
"""
Generate a gitlab CI child pipeline to run multiple integration tests in parallel.
We want to have shorter test execution time.
E.g.
ansible-test integration vm
ansible-test integration vm_info
ansible-test integration vm_disk
...
"""

import os
import jinja2


def main():
    integ_tests = os.listdir("tests/integration/targets")
    j2env = jinja2.Environment(loader=jinja2.FileSystemLoader("ci-infra/gitlab-dynamic-pipeline/"))
    template = j2env.get_template("integration_job.yml.j2")
    with open("child-pipeline-gitlab-ci.yml", "w+") as outf:
        head_content = open("ci-infra/gitlab-dynamic-pipeline/child-pipeline-gitlab-ci.yml.head").read()
        outf.write(head_content)
        for integ_test in integ_tests:
            context = dict(
                integration_test_name=integ_test,
                ci_job_name=f"integ-{integ_test}",
                ci_job_resource_group=f"integ-{integ_test}",
            )
            job_content = template.render(**context)
            outf.write(job_content)


if __name__ == "__main__":
    main()
