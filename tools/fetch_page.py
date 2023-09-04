import requests
import html2text
from readability import Document
from langchain.agents import Tool
from urllib.parse import urlparse, parse_qs, urlunparse
from langchain.text_splitter import RecursiveCharacterTextSplitter


def fetch_page(url, model_name='gpt-3.5-turbo', timeout_sec=10):
    """Tool to fetch the content of a web page from a given URL.
    - This returns `title`, `content`, and `has_next` indicator. `content` is returned in markdown format.
    - By default, only up to 2,000 tokens of content are retrieved.
    - If there is more content available on the page, the `has_next` value will be True.
    - To read the continuation, you can increment the `page` parameter with the same URL and input them again.

    Returns
    -------
    Dict[str, Any]:
    - status: str
    - page_content
      - title: str
      - content: str
      - has_next: bool
    """
    # page parameter
    parsed_url = urlparse(url)
    parsed_qs = parse_qs(parsed_url.query)
    page = int(parsed_qs.get("page", [1])[0]) - 1
    url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", "")
    )

    try:
        response = requests.get(url, timeout=timeout_sec)
        response.encoding = 'utf-8'
    except requests.exceptions.Timeout:
        return {
            "status": 500,
            "page_content": {'error_message': 'Could not download page due to Timeout Error. Please try to fetch other pages.'}
        }

    if response.status_code != 200:
        return {
            "status": response.status_code,
            "page_content": {'error_message': 'Could not download page. Please try to fetch other pages.'}
        }
    
    try:
        doc = Document(response.text)
        title = doc.title()
        html_content = doc.summary()
        content = html2text.html2text(html_content)
    except:
        return {
            "status": 500,
            "page_content": {'error_message': 'Could not parse page. Please try to fetch other pages.'}
        }

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name=model_name,
        chunk_size=1000,
        chunk_overlap=0,
    )
    chunks = text_splitter.split_text(content)
    if page >= len(chunks):
        return {
            "status": 500,
            "page_content": {'error_message': 'page parameter looks invalid. Please try to fetch other pages.'}
        }
    else:
        return {
            "status": 200,
            "page_content": {
                "title": title,
                "content": chunks[page],
                "has_next": page < len(chunks) - 1
            }
        }


def get_fetch_page_tool():
    fetch_page_tool_description = """
    Tool to fetch the content of a web page from a given URL.

    This returns `status` and `page_content` (`title`, `content` and `has_next` indicator).
    If status is not 200, there was some error of fetching page. (Try fetch other pages.)
    If a status code other than 200 is returned, please don't give up and make sure to check other pages.

    By default, only up to 2,000 tokens of content are retrieved. If there is more content available on the page, the `has_next` value will be True.
    To read the continuation, you can increment the `page` parameter with the same URL and input them again. (paging is start with 1, so next page is 2)
    e.g. https://www.obamalibrary.gov/obamas/president-barack-obama?page=2
    """
    return Tool(
        name='fetch_page',
        func=fetch_page,
        description=fetch_page_tool_description
    )
