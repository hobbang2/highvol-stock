
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from langchain.text_splitter import CharacterTextSplitter

def lookup(target_mode:str, news_headers: str)->str:
    llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')

    summary_prompt_template = PromptTemplate(
    input_variables=["target_mode", "information"], template="""
    You are a fund manager AI.
    You need to explain the reasons why a given stock's price {target_mode} based on news headlines.
    If some headlines contain irrelevant content related to the stock, you have to ignore that.
    Also, if some headlines are relevant to another stock with a similar name, you have to ignore that as well.
    I will provide you with the headlines below. Please respond in Korean noun phrases.
    
    header:
    - 플레이디 급등, 레뷰코퍼레이션·이엠넷·모비데이즈 등 광고 관련주 강세
    - [시간외 특징주] 플레이디 주가 기세등등...틱톡 전자상거래 플랫폼 '틱톡샵'...
    - 플레이디, 낮부터 갑작스런 19% 급등…7000원선 재돌파
    - 전자상거래 강세에 전자상거래 플랫폼 강자 플레이디 주가 급등
    
    answer:
    틱톡 전자상거래 플랫폼 '틱톡샵'에 대한 기대
    
    {information}
    """
)
    chain = LLMChain(llm=llm, prompt=summary_prompt_template)

    return chain.run(target_mode = target_mode, information = news_headers)