import React, { useState } from 'react'
import Home from './pages/Home'
import Link from './Link'

function App() {
  const [connectionSuccess, setConnectionSuccess] = useState(false)
  const [responseData, setResponseData] = useState(null)


  const handlePlaidSuccess = async () => {
        setConnectionSuccess(true)
        // Give the backend a moment to sync, or we could poll, but for now just fetch
        // In a real app we might show a loading spinner while initial sync happens
        setTimeout(async () => {
            const text = await fetch('http://127.0.0.1:8000/transactions')
            const data = await text.json()
            setResponseData(data)
        }, 2000) 
  }


  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold text-blue-600 mb-8">AutoBudget</h1>
      
      {connectionSuccess ? (
        <Home data={responseData} />
      ) : (
        <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800">Connect Your Bank</h2>
        
        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            Connect your bank account securely via Plaid to automatically import your transactions.
          </p>
          <Link onSuccessCallback={handlePlaidSuccess} />
        </div>
        </div>
      )}
    </div>
  )
}

export default App
