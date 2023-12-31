import {FC, MouseEvent} from 'react'
import ModeButton from './ModeButton'

export type IModeSelectorProps = {
  modes: string[]
  currentMode: string
  onModeChange: (event: MouseEvent<HTMLButtonElement>) => void
}

const ModeSelector: FC<IModeSelectorProps> = ({modes, currentMode, onModeChange}) => {
  return (
    <div>
      <label className="shadow-card relative inline-flex cursor-pointer select-none items-center justify-center rounded-md bg-white p-1">
        {/* 각 모드에 대한 버튼 생성 */}
        {modes.map(mode => (
          <ModeButton
            key={mode}
            mode={mode}
            currentMode={currentMode}
            onClick={onModeChange}
          />
        ))}
      </label>
    </div>
  )
}

export default ModeSelector
