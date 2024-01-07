# Highvol-Stock
> 천만주 이상 거래되었거나 상한가를 기록한 주식을 정리하는 웹 서비스

![ce62bed0-d429-4d7e-8c08-31d898be1bcc](https://github.com/hobbang2/highvol-stock/assets/46401358/0ddf12ca-116d-4bdc-be61-0e68995ccf53)

## 01. 개요  
천만주 이상 거래되었거나 상한가를 기록한 주식의 정보로 하루의 시황을 정리하고자 함  
${\rightarrow}$ 매일 종목을 찾고 뉴스 검색, 정리의 반복  
${\Rightarrow}$ <strong>이 과정을 자동화해서 보여주는 사이트를 만들어보자!</strong>

## 02. 프로젝트 구조 
![highvol-stock drawio](https://github.com/hobbang2/highvol-stock/assets/46401358/cef957e8-1716-40a7-ace0-1948e3877dd9)

## 03. 결과 
![image](https://github.com/hobbang2/highvol-stock/assets/46401358/35185a69-2795-4552-931d-aed8098a9b9d)

## 04. 개선할 점 
### 1 ) 기간 동안 2번 이상 언급된 주식
- 종목 명을 눌렀을 때, 수집된 정보를 보여주는 방식으로 변경
    - 현재: 종목 명을 누르면 네이버 증권 사이트로 연결

### 2 ) 주식 정보 조회 날짜
- 주말인 경우, 직전 주 금요일의 정보 보여주기
- 휴장인 날은 캘린더에서 선택하지 못하도록 설정

### 3 ) 무관한 뉴스가 수집되는 문제
- 주식과 관련없는 정보가 수집되는 문제
   - `예를 들어` 남성(004270) 주식이 천만주 이상 거래되었거나 상한가를 기록했을 만족했을 경우 ${\rightarrow}$ 60대 남성, 20대 남성 등 성별에 관한 기사가 수집됨 

### 4 ) https 적용 후 배포
