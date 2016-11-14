#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import load

from remote import Remote


def main():
    job = load("remote_test.json")
    re = Remote("marcc")

    for i in range(0, 1000):
        print(re.expect_completion_time("9345628", job["directory"]))


if __name__ == "__main__":
    main()
