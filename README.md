# Web Browsing Agent Sample
## tl;dr
This is a sample Web Browsing Agent app that uses LangChain's `OpenAIFunctionsAgent` and Streamlit's `StreamlitCallbackHandler`.

You can try this out from [this Sample App](https://web-browsing-agent.streamlit.app/) (OpenAI API key required).

https://github.com/naotaka1128/web_bowsing_agent/assets/5688448/259a80ed-8d6a-44c7-8f7d-c910016ad24f

## How it Works
- The agent uses custom-built DuckDuckGo's search tools and a page retrieval tool to perform web browsing to answer users' questions.
- It employs an agent that uses OpenAI Function Calling, ensuring stable operation.
- The agent operates as follows:
  - Considers search keywords based on the users' question
  - Executes the search using the considered keywords
    - The search results include titles, URLs, and snippets
  - Decides which page to view from the search results, retrieves the page content, and reviews the content
    - Writes the final answer if possible; otherwise, retrieves another page if more information is needed
- Of course, it is also possible to ask additional questions to the agent's answers.
- You can also check the details of the agent's operation.

## Prerequisites
- You will need OpenAI's API_KEY

## Details
### Retrieving Page Content
- Utilizes the `from_tiktoken_encoder` function of RecursiveCharacterTextSplitter to fetch content in chunks of 1000 tokens.
  - If the agent wish to obtain more content, add a `page parameter` to fetch the page again
- As it's a prototype, caching has not been implemented
- It uses `readability` and `html2text` to extract the main body of the page
  - Note that `html2text` has a GPL3.0 license, so be cautious
- Some pages on the website load slowly at times, so we have also set up timeouts in requests.

### Model
- Because the number of tokens used can significantly increase when a question and answer interaction occurs, using `gpt-4` or `gpt-3.5-turbo-16k` is recommended.
  - You can select models in sidebar option buttons.

## Reference
- [Streamlit LLM Examples (Chat with Search)](https://github.com/streamlit/llm-examples/blob/main/pages/2_Chat_with_search.py)
  - I learned how to use `StreamlitCallbackHandler` from this code
- [Build and Learn: AI App Development for Beginners: Unleashing ChatGPT API with LangChain & Streamlit](https://www.amazon.com/dp/B0CDXRMDSL)
  - The code for the entire app was inspired by this book
  - Well, I wrote the book, so there's that haha 😎
