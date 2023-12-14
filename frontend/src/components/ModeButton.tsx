import React from 'react'
import {FC, MouseEvent} from 'react'

export type IModeButtonProps = {
  mode: string
  currentMode: string
  onClick: (event: MouseEvent<HTMLButtonElement>) => void
}

const ModeButton: FC<IModeButtonProps> = ({mode, currentMode, onClick}) => (
  <button
    className={`border flex items-center space-x-[6px] py-2 px-[18px] text-sm font-medium ${
      currentMode === mode ? 'text-primary bg-[#f4f7ff]' : 'text-body-color'
    }`}
    onClick={onClick}
    data-mode={mode}>
    <svg width="16" height="16" viewBox="0 0 16 16" className="mr-[6px] fill-current">
      {/* 각 모드에 따른 아이콘 */}
    </svg>
    {mode}
    {/* {mode === 'custom'
      ? 'Custom'
      : `${mode.charAt(0).toUpperCase()}${mode.slice(1)} Mode`} */}
  </button>
)

export default ModeButton
