import React, {ReactNode, useEffect, useState} from 'react'
import {FC, MouseEvent} from 'react'
import {IReferenceNews, IStockData, IPick} from '../data/fetchStocks'
import {useResponsive} from '../contexts'

export type ITableProps = {
  data: any[]
  header: string[]
}

const Table: FC<ITableProps> = ({data, header}) => {
  const screen_size = useResponsive()
  // screen size에 따라 보여주는 뉴스의 개수를 다르게 함
  const refNewsCnt = 'sm' === screen_size ? 1 : 'md' === screen_size ? 3 : 5
  const [sortConfig, setSortConfig] = useState<{
    key: string | null
    direction: 'ascending' | 'descending'
  }>({
    key: null,
    direction: 'ascending'
  })

  // header의 column을 누르면 동작할 sort 함수
  const sortedData = [...data].sort((a, b) => {
    if (sortConfig.key !== null) {
      const keyA = a[sortConfig.key].data
      const keyB = b[sortConfig.key].data
      if (keyA < keyB) return sortConfig.direction === 'ascending' ? -1 : 1
      if (keyA > keyB) return sortConfig.direction === 'ascending' ? 1 : -1
    }
    return 0
  })

  const handleHeaderClick = (key: string) => {
    setSortConfig(prevSortConfig => ({
      key,
      direction:
        prevSortConfig.key === key && prevSortConfig.direction === 'ascending'
          ? 'descending'
          : 'ascending'
    }))
  }
  // 세자리마다 ','를 포함하는 숫자로 변환하는 함수
  const formatNumberWithCommas = (number: number) =>
    number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')

  // 뉴스 날짜 변환
  const formatDate = (targetDate: string) => {
    const inputDate = new Date(targetDate)
    const year = inputDate.getFullYear().toString().slice(2)
    const month = ('0' + (inputDate.getMonth() + 1)).slice(-2)
    const day = ('0' + inputDate.getDate()).slice(-2)
    const dayOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][
      inputDate.getDay()
    ]
    const hours = ('0' + inputDate.getHours()).slice(-2)
    const minutes = ('0' + inputDate.getMinutes()).slice(-2)

    const formattedDate = `${year}-${month}-${day} ${dayOfWeek} ${hours}:${minutes}`
    return formattedDate
  }

  return (
    // <div className="tableContainer shadow-lg m-40 relative overflow-x-auto">
    <table className="text-center	w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
      <thead className="bg-white border-b sticky top-0 text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
        <tr>
          {header.map(item => (
            <th
              onClick={() => handleHeaderClick(item)}
              className="pt-2 pb-2 border hover:text-blue-600">
              {item}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sortedData.map((item: IPick, rowIndex: number) => (
          <tr
            key={rowIndex}
            className="border hover:brightness-90 odd:bg-white even:bg-slate-50 bg-white border-b dark:bg-gray-800 dark:border-gray-700">
            {Object.values(item)
              .filter((curItem: any) => true === curItem.visible)
              .map((elem: any, columnIndex: number) => (
                // (elem: IReferenceNews[] | string | number, columnIndex: number) => (
                <td key={columnIndex} className="pt-2 pb-2 border hover:font-bold">
                  {columnIndex === 0 ? (
                    <a
                      href={`https://finance.naver.com/item/main.naver?code=${item['stock_code']['data']}`}>
                      {elem.data}
                    </a>
                  ) : typeof elem.data === 'object' ? (
                    // 객체인 경우 description 속성을 보여줌
                    elem.data
                      .slice(0, refNewsCnt)
                      .map((newsInfo: IReferenceNews, news_idx: number) => (
                        // <a href={newsInfo['originallink']}>
                        //   {newsInfo['title']}-{newsInfo['pubDate']}
                        //   <br></br>
                        // </a>
                        <a
                          className="hover:text-blue-600"
                          key={news_idx}
                          href={newsInfo['originallink']}
                          dangerouslySetInnerHTML={{
                            __html: `${newsInfo['title']} - ${formatDate(
                              newsInfo['pubDate']
                            )}<br>`
                          }}></a>
                      ))
                  ) : typeof elem.data === 'number' ? (
                    formatNumberWithCommas(elem.data) // 여기서 formatNumberWithCommas 함수를 사용하여 숫자 포맷팅
                  ) : (
                    String(elem.data)
                  )}
                </td>
              ))}
          </tr>
        ))}
      </tbody>
    </table>
    // </div>
  )
}

export default Table
