import config from './config.json'

export type IPeriodStockData = {
  count: number
  stock_name: string
  stock_code: string
  created_at: string[]
  stock_price: string[]
}

export type IReferenceNews = {
  title: string
  originallink: string
  link: string
  description: string
  pubDate: string
}

export type IStockData = {
  stock_name: string
  stock_price: string
  summary: string
  day_change_proportion: string
  increase_rate: number
  trade_volume: number
  stock_code: string
  sosok: number
  reference_news: IReferenceNews[]
}

interface IPickItem {
  data: string | number | IReferenceNews[] | boolean
  visible: boolean
}
export type IVisibe = {
  // data: string | number | IReferenceNews[]
  // visible: boolean
  [key: string]: string | number | IReferenceNews[] | boolean | boolean
}

// 하드코딩
export type IPick = {
  [key: string]: IVisibe
  '주식 이름': IVisibe
  '주식 가격 (원)': IVisibe
  '거래량 (주)': IVisibe
  '상승률 (%)': IVisibe
  요약: IVisibe
  '연관 뉴스': IVisibe
  stock_code: IVisibe
  sosok: IVisibe
}

const convertStocks = (result: IStockData[]): IPick[] => {
  return result.map(stock => ({
    '주식 이름': {data: stock.stock_name, visible: true},
    '주식 가격 (원)': {data: parseFloat(stock.stock_price), visible: true},
    '거래량 (주)': {data: stock.trade_volume, visible: true},
    '상승률 (%)': {data: stock.increase_rate, visible: true},
    요약: {data: stock.summary, visible: false},
    '연관 뉴스': {data: stock.reference_news, visible: true},
    stock_code: {data: stock.stock_code, visible: false},
    sosok: {data: stock.sosok, visible: false}
  }))
}

const convertPeriodStock = (
  result: IPeriodStockData[]
): {html: string; detail_info: IPeriodStockData[]} => {
  const html = result.reduce((acc: string, cur: IPeriodStockData): string => {
    console.log(cur)
    const stock_html = `<a  href=https://finance.naver.com/item/main.nhn?code=${cur.stock_code} title="hi">${cur.stock_name}(${cur.count})\t</a>`
    return acc + stock_html
  }, '')

  // tooltip에 사용할 정보
  const detail_info = result.map(stock => ({
    count: stock.count,
    stock_name: stock.stock_name,
    stock_code: stock.stock_code,
    created_at: stock.created_at,
    stock_price: stock.stock_price
  }))

  return {
    html: html,
    detail_info: detail_info
  }
}

// 하드코딩
// export type IPick = {
//   '주식 이름': string
//   '주식 가격 (원)': number
//   '거래량 (주)': number
//   '상승률 (%)': number
//   요약: string
//   '연관 뉴스': IReferenceNews[]
//   stock_code: string
//   sosok: number
// }

// const convertStocks = (result: IStockData[]) => {
//   return result.map(stock => ({
//     '주식 이름': stock.stock_name,
//     '주식 가격 (원)': parseFloat(stock.stock_price),
//     '거래량 (주)': stock.trade_volume,
//     '상승률 (%)': stock.increase_rate,
//     요약: stock.summary,
//     '연관 뉴스': stock.reference_news,
//     stock_code: stock.stock_code,
//     sosok: stock.sosok
//   }))
// }

export const fetchStocks = (today: string): Promise<IPick[]> =>
  new Promise((resolve, reject) => {
    fetch(`${config.apiBaseUrl}${config.endpoints.stocks}/${today}`)
      .then(res => res.json())
      .then((data: unknown) => {
        const result = convertStocks(data as IStockData[])
        resolve(result)
      })
      .catch(reject)
  })

export const fetchPeriodStocks = (
  period: number
): Promise<{html: string; detail_info: IPeriodStockData[]}> =>
  new Promise((resolve, reject) => {
    fetch(`${config.apiBaseUrl}${config.endpoints.historicalStocks}/${period}`)
      .then(res => res.json())
      .then((data: unknown) => {
        const result = convertPeriodStock(data as IPeriodStockData[])
        resolve(result)
      })
      .catch(reject)
  })
