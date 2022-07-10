# supreme-fortnight

### Pre-requisites to run the script

1. You must install `Python 3.10`
2. You must install the `pip` packages in your virtual environment. Packages are listed in `source/requirements.txt`
3. You must signup for Mailgun service to send email to intrested recipients
4. Interested recipients must be added to **Authorized Recipients** in Mailgun service
5. Set environment vairables - `MAILGUN_API`, `MAILGUN_API_KEY`, `MAILGUN_FROM`
    - MacOS & Linux
    ```zsh
    export MAILGUN_API=
    ```

    ```zsh
    export MAILGUN_API_KEY=
    ```

    ```zsh
    export MAILGUN_FROM=
    ```
    
    - Windows
    ```pwsh
    set MAILGUN_API=
    ```

    ```pwsh
    set MAILGUN_API_KEY=
    ```

    ```pwsh
    set MAILGUN_FROM=
    ```
    
6. Optionally, you can set right log `level` for your python to read what is happening in the backend

### Pre-requisites to develop

Please follow the steps mentioned in earlier step but use the devcontainer to auto setup docker based developer workspace. If you are using other method please ensure you use `source/requirements-dev.txt`

## Commands to run the script

1. Get Help
```python
python3 send_cloc_report.py -h
```

2. Scan a repo and stdout the report

```python
python3 send_cloc_report.py https://github.com/prnam/learn-python.git
```

2. Scan a repo and send report to email address specified

```python
python3 send_cloc_report.py https://github.com/prnam/learn-python.git -e abc@efg.com xyz@abc.in
```
