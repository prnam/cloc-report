"""Process lines of code in a repo and send the generated report to an email address"""
from __future__ import absolute_import

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Optional

import requests
from shellescape import quote

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
GIT_REGEX = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(\/\/)?)([\w\.@\:\/\-~]+)(\.git)(\/)?"
MAILGUN_API = os.getenv("MAILGUN_API")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_FROM = os.getenv("MAILGUN_FROM")


def clone_git_repo(repo_url: str, emails: list):
    """Clone git repo"""
    with TemporaryDirectory() as tmp_dir:
        logging.info("Current working directoy: %s", os.getcwd())
        current_working_directory = os.getcwd()
        logging.info("Changing the directory....")
        os.chdir(tmp_dir)
        logging.info("Current working directoy: %s", os.getcwd())
        temporary_working_directory = os.getcwd()
        clone_command = f"git clone {quote(repo_url)}"
        logging.info("Cloning repo using the command: %s", clone_command)
        os.system(clone_command)
        pygount_scan(current_working_directory, emails,
                     temporary_working_directory)
        logging.info("Deleting the %s directory....", tmp_dir)


def pygount_scan(cwd: str, emails: list, temporary_working_directory: str):
    """Scan the repo cloned and write the generate report to a file"""
    repo_name = "".join(os.listdir())
    command = f"pygount --format=summary {quote(repo_name)}"
    result = subprocess.check_output(command, shell=True).decode("utf-8")
    save_to_file = f"cloc-report-{repo_name.lower()}.txt"
    with open(save_to_file, "w", encoding="utf-8") as file:
        file.write(result)
    if emails is not None:
        response = send_email(save_to_file, repo_name, emails,
                              temporary_working_directory)
        if response.status_code == 200:
            logging.info("Email sent successfully")
            print("Email sent successfully")
        else:
            logging.warning("Failed to send email to the requested recipients")
            logging.info(
                "Please check mail service configuration and status page")
            logging.info("Copying the report to your local persistent storage")
            shutil.copy2(save_to_file, cwd)
            logging.info("Report stored at %s with file name %s", cwd,
                         save_to_file)
            print(f"Report stored at {cwd} with file name {save_to_file}")
    logging.debug("---- CLoC report for '%s' repo ----", repo_name)
    logging.debug(read_file(save_to_file, temporary_working_directory))
    print(f"---- CLoC report for '{repo_name}' repo ----")
    print(read_file(save_to_file, temporary_working_directory))


def read_file(filename: str, temporary_working_directory: str):
    """Read files"""
    absolute_path = f"{quote(temporary_working_directory)}/{quote(filename)}"
    with open(absolute_path, "r", encoding="utf-8") as file:
        return file.read()


def send_email(report: str, repo_name: str, to_recipients: list,
               temporary_working_dir: str):
    """Send the report to email address"""
    logging.info("Preparing email....")
    print("Preparing email....")
    content = read_file(report, temporary_working_dir)
    logging.info("File is been read to email text")
    try:
        return requests.post(
            MAILGUN_API,
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": MAILGUN_FROM,
                "to": to_recipients,
                "subject": f'---- CLoC report for "{repo_name}" repo ----',
                "text": {content},
            },
        )
    except requests.exceptions.HTTPError as http_error:
        logging.error(http_error)
        print("HTTP error while connecting to your mail service")
        sys.exit(1)
    except requests.exceptions.ConnectionError as connection_error:
        logging.error(connection_error)
        print("Connection Error while connecting to your mail service")
        sys.exit(1)
    except requests.exceptions.Timeout as timeout_error:
        logging.error(timeout_error)
        print("Timeout Error while connecting to your mail service")
        sys.exit(1)
    except requests.exceptions.RequestException as request_exception_error:
        logging.error(request_exception_error)
        print("Unknown error while connecting to your mail service")
        print("Please check mail service configuration and status page")
        sys.exit(1)


def argument_parser():
    """Collect input values from the arguments"""
    parser = argparse.ArgumentParser(
        prog="send-cloc-report",
        description="CLOC in a repo and send the generated report to an email address",
    )
    parser.add_argument("repo",
                        action="store",
                        type=str,
                        help="enter the remote git repo url",
                        nargs=1)

    parser.add_argument(
        "-e",
        "--email",
        dest="email",
        metavar="EMAIL-ADDRESS",
        action="store",
        type=str,
        help="enter the email address you want to send the report",
        nargs="+",
    )
    args = parser.parse_args()
    repo = "".join(args.repo)
    return repo, args.email


def input_validation(repo: str, emails: Optional[list] = None):
    """Validates inputs provided via the arguments"""
    if not re.match(GIT_REGEX, repo):
        logging.error("Invalid repo url!!!")
        sys.exit(1)
    if emails is None:
        return repo, None
    for email in emails:
        if not re.match(EMAIL_REGEX, email):
            logging.error(
                "One of the email is invalid, please fix it and re try!!!")
            sys.exit(1)
    return repo, emails


def main():
    """Invoking main method to intitate the program"""
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        filename="myapp.log",
        level=logging.DEBUG,
    )
    logging.info("Program started....")
    args_parser_result = argument_parser()
    if args_parser_result[1] is None:
        input_validation_result = input_validation(args_parser_result[0])
    else:
        input_validation_result = input_validation(args_parser_result[0],
                                                   args_parser_result[1])
    clone_git_repo(input_validation_result[0], input_validation_result[1])
    print("Program completed gracefully")
    logging.info("Program completed gracefully")


if __name__ == "__main__":
    main()
