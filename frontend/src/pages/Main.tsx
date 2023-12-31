import React, {FC, useState, MouseEvent, useEffect} from 'react'
import ModeButton from '../components/ModeButton'
import ModeSelector from '../components/ModeSelector'
import {
  IPeriodStockData,
  IPick,
  IStockData,
  fetchPeriodStocks,
  fetchStocks
} from '../data'
import {
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable
} from '@tanstack/react-table'
import Table from '../components/Table'
import {NoticeCard} from '../components'

import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import {start} from 'repl'

const Main: FC = () => {
  const [mode, setMode] = useState<string>('전체보기')
  const [period, setPeriod] = useState<string>('0')
  const [currentData, setCurrentData] = useState<IPick[]>([])
  const [periodData, setPeriodData] = useState<{
    html: string
    detail_info: IPeriodStockData[]
  }>({html: '', detail_info: []})
  const [originData, setOriginData] = useState<IPick[]>([])
  const [currentHeader, setCurrentHeader] = useState<string[]>([])

  const handleButtonClick = (event: MouseEvent<HTMLButtonElement>) => {
    const newMode = event.currentTarget.getAttribute('data-mode') || ''
    setMode(newMode)

    if ('전체' === newMode) {
      setCurrentData(originData)
    } else if ('KOSDAQ' === newMode) {
      setCurrentData(originData.filter(item => item.sosok.data === 1))
    } else if ('KOSPI' === newMode) {
      setCurrentData(originData.filter(item => item.sosok.data === 0))
    } else {
      // nothing
    }
  }

  const handleButtonPeriod = (event: MouseEvent<HTMLButtonElement>) => {
    const newPeriod = event.currentTarget.getAttribute('data-mode') || ''

    if (period == newPeriod) {
      return
    }
    setPeriod(newPeriod)
    const cur_period = parseInt(newPeriod)
    console.log(cur_period)
    fetchPeriodStocks(cur_period)
      .then(response => {
        setPeriodData(response)
      })
      .catch(error => {
        // 에러 처리
        console.error('API 호출 중 에러:', error)
      })
      .finally()
  }

  /**
   * YYYY-MM-DD 형식의 현재 날짜 데이터를 얻는 함수
   * @returns YYYY-MM-DD 형식의 현재 날짜 데이터
   */
  const parseDate = (today: Date): string => {
    const year = today.getFullYear()
    const month = (today.getMonth() + 1).toString().padStart(2, '0')
    const day = today.getDate().toString().padStart(2, '0')

    const dateString = year + '-' + month + '-' + day

    return dateString
  }
  // API로부터 받아온 데이터를 저장할 상태
  const [data, setData] = useState<IPick[] | null>(null)
  const [startDate, setStartDate] = useState<Date>(new Date())

  const isWeekday = (date: Date): boolean => {
    const day = date.getDay()
    return day !== 0 && day !== 6
  }

  const pickData = (date: Date) => {
    if (null === date) return
    setStartDate(date)
  }

  useEffect(() => {
    // API 엔드포인트 URL
    fetchStocks(parseDate(startDate))
      .then(response => {
        setCurrentData(response || [])
        setOriginData(response || [])

        // stock data가 있는 경우에만 table header 설정
        if (response.length > 0) {
          setCurrentHeader(
            Object.keys(response[0]).filter(
              (item: string) => response[0][item].visible === true
            ) || []
          )
        }
      })
      .catch(error => {
        // 에러 처리
        console.error('API 호출 중 에러:', error)
      })
      .finally()
  }, [startDate]) // 빈 배열을 넣어 한 번만 호출되도록 설정

  return (
    <div className="ml-40 mr-40 mt-10 relative">
      <ModeSelector
        modes={['1주', '4주', '52주']}
        currentMode={period}
        onModeChange={handleButtonPeriod}></ModeSelector>

      <NoticeCard
        title={
          '0' === period
            ? '2번 이상 언급된 주식 조회하기'
            : `${period}간 2번 이상 언급된 주식`
        }
        content={periodData.html}></NoticeCard>
      {/* <DatePicker selected={startDate} onChange={date => setStartDate(date)} /> */}
      <DatePicker
        className="mt-1 mb-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        // showIcon
        selected={startDate}
        filterDate={isWeekday}
        onChange={pickData}
      />
      <ModeSelector
        modes={['전체', 'KOSPI', 'KOSDAQ']}
        currentMode={mode}
        onModeChange={handleButtonClick}></ModeSelector>
      <div className="mt-2 mb-2">총 {currentData.length} 개</div>
      <div className="shadow-lg tableContainer">
        {currentData.length > 0 && (
          <Table data={currentData} header={currentHeader}></Table>
        )}
        {currentData.length == 0 && (
          <NoticeCard
            className="mt-3"
            title={`${parseDate(startDate)} 해당 날짜에 데이터가 없습니다.`}
            content=""></NoticeCard>
        )}
      </div>
    </div>
  )
}

export default Main
