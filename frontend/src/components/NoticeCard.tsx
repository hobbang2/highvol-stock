import type {FC, DetailedHTMLProps, HTMLAttributes} from 'react'
import {makeClassName} from './textUtils'
import {SmallTitle} from './Texts'

export type INoticeCardProps = {
  backgroundColor?: string
  title: string
  content: string
  className?: string
  numberOfLines?: number
  html?: string
}

export const NoticeCard: FC<INoticeCardProps> = ({
  backgroundColor,
  title,
  content,
  className,
  numberOfLines,
  html,
  ...props
}) => {
  const cardClassName = makeClassName(
    `max-w p-6 bg-white border border-gray-200 rounded-lg `,
    className,
    numberOfLines
  )

  // content에 HTML이 있는지 확인
  const hasHtmlContent = /<[^>]+>/g.test(content)

  return (
    <div {...props} className={cardClassName}>
      <SmallTitle>{title}</SmallTitle>
      {hasHtmlContent ? (
        <p
          className="mb-3 font-normal text-gray-500 dark:text-gray-400"
          dangerouslySetInnerHTML={{__html: content}}></p>
      ) : (
        <p className="mb-3 font-normal text-gray-500 dark:text-gray-400">{content}</p>
      )}
    </div>
  )
}
