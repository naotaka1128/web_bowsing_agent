from itertools import islice
from langchain.agents import Tool
from duckduckgo_search import DDGS


def search_ddg(query, max_result_num=5):
    """
    Tool for performing DuckDuckGo searches
    - Please enter the keyword you want to search for and use it.
    - The title, snippet (description), and URL of each page in the search results will be returned.
    
    Sample Response of DuckDuckGo python library
    --------------------------------------------
    [
        {
            'title': '日程・結果｜Fifa 女子ワールドカップ オーストラリア&ニュージーランド 2023｜なでしこジャパン｜日本代表｜Jfa｜日本サッカー協会',
            'href': 'https://www.jfa.jp/nadeshikojapan/womensworldcup2023/schedule_result/',
            'body': '日程・結果｜FIFA 女子ワールドカップ オーストラリア&ニュージーランド 2023｜なでしこジャパン｜日本代表｜JFA｜日本サッカー協会. FIFA 女子ワールドカップ. オーストラリア&ニュージーランド 2023.'
        }, ...
    ]

    Returns
    -------
    List[Dict[str, str]]:
    - title
    - snippet
    - url
    """
    res = DDGS().text(query, region='wt-wt', safesearch='off', backend="lite")
    return [
        {
            "title": r.get('title', ""),
            "snippet": r.get('body', ""),
            "url": r.get('href', "")
        }
        for r in islice(res, max_result_num)
    ]


def get_search_ddg_tool():
    search_tool_description = """
    Tool for performing DuckDuckGo searches.
    Please enter the keyword you want to search for and use it.
    The title, snippet (description) and URL of each page in the search results will be returned.
    The information available through this tool is QUITE CONDENSED and sometimes outdated.

    If you can't find the information you're looking for, please make sure to use the `WEB Page Fetcher` tool to read the content of each page.
    Feel free to use the most appropriate language for the context. (not necessary same as the user's language)
    For example, for programming-related questions, it's best to search in English.
    """
    return Tool(
        name='search_ddg',
        func=search_ddg,
        description=search_tool_description
    )
