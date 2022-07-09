"""Process lines of code in a repo and send the generated report to an email address"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

import requests

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
GIT_REGEX = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(\/\/)?)([\w\.@\:\/\-~]+)(\.git)(\/)?"
MAILGUN_API = "https://api.mailgun.net/v2/samples.mailgun.org/messages"

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
REPO = "".join(args.repo)

if not re.match(GIT_REGEX, REPO):
    print("Invalid repo url!!!")
    sys.exit(1)

for item in args.email:
    if not re.match(EMAIL_REGEX, item):
        print("One of the email is invalid, please fix it and re try!!!")
        sys.exit(1)
    else:
        EMAILS = ",".join(item)


def clone_git_repo(repo_url):
    """Clone git repo"""
    with TemporaryDirectory() as tmp_dir:
        print(f"Current working directoy: {os.getcwd()}")
        cwd = os.getcwd()
        print("Changing the directory....")
        os.chdir(tmp_dir)
        print(f"Current working directoy: {os.getcwd()}")
        clone = f"git clone {repo_url}"
        print(f"Cloning repo using the command: {clone}")
        os.system(shlex.quote(clone))
        pygount_scan(cwd)
        print(f"Deleting the {tmp_dir} directory....")


def pygount_scan(cwd):
    """Scan the repo cloned and write the generate report to a file"""
    repo_name = "".join(os.listdir())
    command = f"pygount --format=summary {repo_name}"
    result = subprocess.check_output(shlex.quote(command),
                                     shell=True).decode("utf-8")
    file = "report.txt"
    with open(file, "w", encoding="utf-8") as file:
        file.write(result)

    shutil.copy2(file, cwd)
    print(f"---- CLOC Report for '{repo_name}' repo ----")
    with open(file, "r", encoding="utf-8") as file:
        print(file.read())
    send_email(file=file, to_recipient=EMAILS, repo_name=repo_name)


def send_email(file, to_recipient, repo_name):
    """Send report to necessary recevipents"""
    print(
        requests.post(
            MAILGUN_API,
            auth=("api", "key-3ax6xnjp29jd6fds4gc373sgvjxteol0"),
            files=[("attachment", open(file, encoding="utf-8"))],
            data={
                "from": "Excited User <me@samples.mailgun.org>",
                "to": to_recipient,
                "subject": f"---- CLOC Report for '{repo_name}' repo ----",
                "text": "Testing some Mailgun awesomness!",
                "html": "<html>HTML version of the body</html>",
            },
        ))


clone_git_repo(REPO)
