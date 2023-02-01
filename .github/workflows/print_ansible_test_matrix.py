#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json


# run: echo "::set-output name=matrix::{\"node\":[10, 12, 14]}"
def main():
    ansible_python_versions = {
        "stable-2.9": ["3.8"],
        "stable-2.10": ["3.8", "3.9"],
        "stable-2.11": ["3.8", "3.9"],
        "stable-2.12": ["3.8", "3.9", "3.10"],
        "stable-2.13": ["3.8", "3.9", "3.10"],
        "stable-2.14": ["3.9", "3.10", "3.11"],
    }
    matrix = dict()
    matrix["include"] = list()

    # Run sanity tests only on latest 3 ansible version (the supported one)
    # and for each only on latest python version
    ansible_python_versions_list = list(ansible_python_versions.keys())
    testing_type = "sanity"
    for ansible_version in ansible_python_versions_list[-3:]:
        python_version = ansible_python_versions[ansible_version][-1]
        matrix["include"].append(dict(
            ansible=ansible_version,
            python=python_version,
            testing_type=testing_type,
        ))

    # Run units test on all possible ansi-py combinations
    testing_type = "units"
    for ansible_version in ansible_python_versions:
        for python_version in ansible_python_versions[ansible_version]:
            matrix["include"].append(dict(
                ansible=ansible_version,
                python=python_version,
                testing_type=testing_type,
            ))

    print("version_matrix=" + json.dumps(matrix))


main()
