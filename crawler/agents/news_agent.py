
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import LLMChain

from langchain.agents import initialize_agent, Tool, AgentType
from tools.tools import  get_news_summary
from langchain.text_splitter import CharacterTextSplitter

def lookup(news_headers: str)->str:
    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')

    summary_prompt_template = PromptTemplate(
    input_variables=["information"], template="""
    You are fund manager AI. 
    You need to find reason why given stock increase from news header.
    If some headers contain irrelevant content with the stock, you can ignore that.
    I give you headers below. Give me answer with Korean.
    
    header:
    - 플레이디 급등, 레뷰코퍼레이션·이엠넷·모비데이즈 등 광고 관련주 강세 - 23-12-28 Thu 09:54
    - [시간외 특징주] 플레이디 주가 기세등등...틱톡 전자상거래 플랫폼 '틱톡샵'... - 23-12-28 Thu 03:12
    - 플레이디, 낮부터 갑작스런 19% 급등…7000원선 재돌파 - 23-12-27 Wed 14:56
    
    answer:
    틱톡 전자상거래 플랫폼 '틱톡샵'에 대한 기대
    
    {information}
    """
)
    # chain = load_summarize_chain(llm, chain_type="stuff",prompt=summary_prompt_template)
    chain = LLMChain(llm=llm, prompt=summary_prompt_template)

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=0
    )
    split_docs = text_splitter.create_documents(news_headers)
   
    return chain.run(information = news_headers)