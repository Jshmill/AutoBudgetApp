import React, { useState, useEffect } from 'react';
import './Home.scss';

const COLUMNS = [
  { key: 'id', label: 'ID' },
  { key: 'date', label: 'Date' },
  { key: 'description', label: 'Description' },
  { key: 'amount', label: 'Amount' },
  { key: 'category', label: 'Category' },
  { key: 'source', label: 'Source' },
];

const Home = () => {
  const [data, setData] = useState([]);
  const [totalCost, setTotalCost] = useState(null);
  const [balances, setBalances] = useState([]);

  useEffect(() => {
    const fetchBalances = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/balances');
        const responseData = await response.json();
        if (Array.isArray(responseData)) {
          setBalances(responseData);
        } else {
             console.log("Balance fetch error or no account:", responseData);
        }
      } catch (error) {
        console.error("Error fetching balances:", error);
      }
    };
    fetchBalances();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('http://127.0.0.1:8000/transactions');
      const responseData = await response.json();
      setData(responseData);
    };
    fetchData();
  }, []);

  useEffect(() => {
    const fetchTotalCost = async () => {
      const response = await fetch('http://127.0.0.1:8000/transactions/totalcost');
      const responseData = await response.json();
      setTotalCost(responseData);
    };
    fetchTotalCost();
  }, []);

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>

      <div className="table-container">
        <h3>Transaction Data:</h3>

        {data.length > 0 ? (
          <table className="transaction-table">
            <thead>
              <tr>
                {COLUMNS.map(col => (
                  <th key={col.key}>{col.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((item) => (
                <tr key={item.id}>
                  {COLUMNS.map(col => (
                    <td key={col.key}>
  {col.key === 'amount'
    ? `$${Number(item[col.key]).toFixed(2)}`
    : item[col.key]}
</td>

                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No data available</p>
        )}

        <h3>Account Balances:</h3>
        <div className="balance-container">
          {balances.length > 0 ? (
            <div className="balance-grid">
              {balances.map((account, index) => (
                <div key={index} className="balance-card">
                  <h4>{account.name}</h4>
                  <p>Current: ${account.current_balance}</p>
                  <p className="sub-text">Available: ${account.available_balance}</p>
                  <p className="account-type">{account.subtype}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>No account linked or balance data unavailable.</p>
          )}
        </div>

        <h3>Total Cost:</h3>
        <div className="total-cost">
          {totalCost !== null ? `$${totalCost}` : 'No data available'}
        </div>
      </div>
    </div>
  );
};

export default Home;
