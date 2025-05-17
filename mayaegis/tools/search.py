from bs4 import BeautifulSoup
from langchain_community.tools import BraveSearch
import string
import re
import os
import json
from crewai_tools import tool

def remove_html(content):
    oline = content
    soup = BeautifulSoup(oline, "html.parser")
    for data in soup(["style", "script"]):
        data.decompose()
    tmp = " ".join(soup.stripped_strings)
    tmp = "".join(filter(lambda x: x in set(string.printable), tmp))
    tmp = re.sub(" +", " ", tmp)
    return tmp

brave_tool = BraveSearch.from_api_key(
    api_key=os.getenv("BRAVE_API_KEY"), search_kwargs={"count": 20}
)

@tool("SearchEngine")
def search_engine(query: str) -> str:
    """
    Search-Engine tool for browsing the web and getting urls, titles, and website snippets

    Parameters:
    - query (str): Query that will be sent to the search engine

    Returns:
    - str: The search result from the query containing the "Title", "Link", and "Snippet" for each search result
    """

    response = json.loads(brave_tool.run(query))

    output = ""
    for entry in response:
        output += f"TITLE:   {entry.get('title')}\n"
        output += f"LINK:    {entry.get('link')}\n"
        output += f"SNIPPET: {remove_html(entry.get('snippet'))}\n"
        output += "\n\n"

    return output[:-4]


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from bs4 import BeautifulSoup
# import string
# import re
# import time


# def remove_html(content):
#     soup = BeautifulSoup(content, "html.parser")
#     for data in soup(["style", "script"]):
#         data.decompose()
#     tmp = " ".join(soup.stripped_strings)
#     tmp = "".join(filter(lambda x: x in set(string.printable), tmp))
#     tmp = re.sub(" +", " ", tmp)
#     return tmp


# def search_engine_selenium(query: str) -> str:
#     """
#     Performs a search query using Brave Search via Selenium and retrieves results in the same format.

#     Parameters:
#     - query (str): The search query to be sent to Brave Search.

#     Returns:
#     - str: Formatted search results with title, link, and snippet.
#     """

#     # Set up Selenium WebDriver (Ensure you have installed the required driver, e.g., ChromeDriver)
#     service = Service("path/to/chromedriver")  # Replace with the path to your WebDriver
#     driver = webdriver.Chrome(service=service)

#     try:
#         # Open Brave Search
#         driver.get("https://search.brave.com/")
#         time.sleep(2)  # Wait for the page to load

#         # Find the search bar and input the query
#         search_bar = driver.find_element(By.NAME, "q")
#         search_bar.send_keys(query)
#         search_bar.send_keys(Keys.RETURN)
#         time.sleep(2)  # Wait for the results to load

#         # Scrape search results
#         results = driver.find_elements(By.CSS_SELECTOR, ".snippet.fdb")  # Update selector if needed
#         output = ""

#         for result in results:
#             # Extract title
#             title_element = result.find_element(By.CSS_SELECTOR, ".snippet-title")
#             title = title_element.text if title_element else "No title"

#             # Extract link
#             link_element = title_element.find_element(By.TAG_NAME, "a")
#             link = link_element.get_attribute("href") if link_element else "No link"

#             # Extract snippet
#             snippet_element = result.find_element(By.CSS_SELECTOR, ".snippet-description")
#             snippet = snippet_element.text if snippet_element else "No snippet"

#             # Clean and format the snippet
#             snippet_cleaned = remove_html(snippet)

#             # Append to output
#             output += f"TITLE:   {title}\n"
#             output += f"LINK:    {link}\n"
#             output += f"SNIPPET: {snippet_cleaned}\n"
#             output += "\n\n"

#         return output[:-4]  # Remove extra newlines at the end

#     finally:
#         # Quit the browser
#         driver.quit()


# # Example usage
# if __name__ == "__main__":
#     query = input("Enter your search query: ")
#     results = search_engine_selenium(query)
#     print(results)
