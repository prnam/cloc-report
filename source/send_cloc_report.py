"""Process lines of code in a repo and send the generated report to an email address"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from shellescape import quote

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
GIT_REGEX = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(\/\/)?)([\w\.@\:\/\-~]+)(\.git)(\/)?"
MAILGUN_API = "https://api.mailgun.net/v2/samples.mailgun.org/messages"

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
        clone_command = "git clone {}".format(quote(repo_url))
        print(f"Cloning repo using the command: {clone_command}")
        os.system(clone_command)
        pygount_scan(cwd)
        print(f"Deleting the {tmp_dir} directory....")


def pygount_scan(cwd):
    """Scan the repo cloned and write the generate report to a file"""
    repo_name = "".join(os.listdir())
    command = "pygount --format=summary {}".format(quote(repo_name))
    result = subprocess.check_output(command, shell=True).decode("utf-8")
    save_to_file = "report.txt"
    with open(save_to_file, "w", encoding="utf-8") as file:
        file.write(result)

    shutil.copy2(save_to_file, cwd)
    print(f"---- CLOC Report for '{repo_name}' repo ----")
    with open(save_to_file, "r", encoding="utf-8") as file:
        print(file.read())


clone_git_repo(REPO)
