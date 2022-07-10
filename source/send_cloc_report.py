"""Process lines of code in a repo and send the generated report to an email address"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import logging
import requests
from shellescape import quote

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
GIT_REGEX = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(\/\/)?)([\w\.@\:\/\-~]+)(\.git)(\/)?"
MAILGUN_API = os.environ.get("MAILGUN_API")
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_FROM = os.environ.get("MAILGUN_FROM")


def clone_git_repo(repo_url: str, emails: list):
    """Clone git repo"""
    with TemporaryDirectory() as tmp_dir:
        logging.info("Current working directoy: %s", os.getcwd())
        cwd = os.getcwd()
        logging.info("Changing the directory....")
        os.chdir(tmp_dir)
        logging.info("Current working directoy: %s", os.getcwd())
        clone_command = f"git clone {quote(repo_url)}"
        logging.info("Cloning repo using the command: %s", clone_command)
        os.system(clone_command)
        pygount_scan(cwd, emails)
        logging.info("Deleting the %s directory....", tmp_dir)


def pygount_scan(cwd: str, emails: list):
    """Scan the repo cloned and write the generate report to a file"""
    repo_name = "".join(os.listdir())
    command = f"pygount --format=summary {quote(repo_name)}"
    result = subprocess.check_output(command, shell=True).decode("utf-8")
    save_to_file = f"cloc-report-{repo_name.lower()}.txt"
    with open(save_to_file, "w", encoding="utf-8") as file:
        file.write(result)
    response = send_email(save_to_file, repo_name, emails)
    if response.status_code == 200:
        logging.info("Email sent successfully")
    else:
        logging.warning("Failed to send email to the requested recipients")
        logging.info("Please check mail service configuration and status page")
        logging.info("Copying the report to your local persistent storage")
        shutil.copy2(save_to_file, cwd)
        logging.info("Report stored at %s with file name %s", cwd, save_to_file)
    logging.debug("---- CLOC Report for %s repo ----", repo_name)
    with open(save_to_file, "r", encoding="utf-8") as file:
        logging.debug(file.read())


def send_email(report: str, repo_name: str, to_recipients: list):
    """Send the report to email address"""
    logging.info("Preparing email....")
    with open(report, encoding="utf-8") as file:
        content = file.read()
    logging.info("File is been read to email text")
    return requests.post(
        MAILGUN_API,
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": MAILGUN_FROM,
            "to": to_recipients,
            "subject": f'---- CLOC Report for "{repo_name}" repo ----',
            "text": {content},
        },
    )


def argument_parser():
    """Collect input values from the arguments"""
    parser = argparse.ArgumentParser(
        prog="send-cloc-report",
        description="CLOC in a repo and send the generated report to an email address",
    )
    parser.add_argument(
        "repo", action="store", type=str, help="enter the remote git repo url", nargs=1
    )

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


def input_validation(repo: str, emails: list):
    """Validates inputs provided via the arguments"""
    if not re.match(GIT_REGEX, repo):
        logging.error("Invalid repo url!!!")
        sys.exit(1)

    for email in emails:
        if not re.match(EMAIL_REGEX, email):
            logging.error("One of the email is invalid, please fix it and re try!!!")
            sys.exit(1)
    return repo, emails


def main():
    """Invoking main method to intitate the program"""
    args_parser_result = argument_parser()
    input_validation_result = input_validation(
        args_parser_result[0], args_parser_result[1]
    )
    clone_git_repo(input_validation_result[0], input_validation_result[1])


if __name__ == "__main__":
    main()
