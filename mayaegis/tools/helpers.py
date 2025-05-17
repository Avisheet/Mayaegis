from datetime import datetime
import pytz
import platform
import requests
import subprocess
from crewai_tools import tool


@tool("CurrentISTTime")
def current_ist_timestamp():
    """
    Generates the current time's timestamp in UTC.

    Returns:
    - string: Current timestamp in UTC
    """
    ist = pytz.timezone("Asia/Kolkata")
    utc_now = datetime.now(ist)
    return utc_now.strftime("%Y-%m-%d %H:%M:%S %Z")


@tool("PingIP")
def ping_ip(hostname):
    """
    Check if an IP exists/responding by using the "ping" command

    Returns:
    - boolean: rather or not the IP/address exists or is responding
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", hostname]
    response = subprocess.run(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return response.returncode == 0


@tool("MyIP")
def my_ip():
    """Get external ip address or provide one"""

    """
    Get current client's public IP address

    Returns:
    - str: The results of the Nettacker scan or an error message.
    """

    response = requests.get("https://api.ipify.org", timeout=15)
    return str(response.text)


@tool("Nmap")
def nmap(target: str, options: str = "") -> str:
    """
    Executes nmap commands and returns the network scan results.

    Parameters:
    - target (str): The IP address, hostname, or network to scan.
    - options (str): Additional command-line options for nmap.
    """

    if not target:
        raise ValueError("Target is required for nmap scanning.")

    command = f"nmap {options} {target}"

    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error executing nmap: {stderr.decode('utf-8')}")

    return stdout.decode("utf-8")


# print(UtilityTools.my_ip())
