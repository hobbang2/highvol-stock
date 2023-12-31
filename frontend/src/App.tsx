import React from 'react'
import './App.css'
import {ResponsiveProvider} from './contexts'
import Main from './pages/Main'

const App: React.FC = () => {
  return (
    <ResponsiveProvider>
      <div className="App">
        <Main></Main>
      </div>
    </ResponsiveProvider>
  )
}

export default App
