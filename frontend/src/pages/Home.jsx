import React, { useState, useEffect } from 'react';
import './Home.scss';

const Home = () => {
  const [data, setData] = useState([]);
  const [totalCost, setTotalCost] = useState(null);

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
                {Object.keys(data[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index}>
                  {Object.values(item).map((value, idx) => (
                    <td key={idx}>{value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No data available</p>
        )}

        <h3>Total Cost:</h3>
        <div className="total-cost">
          {totalCost !== null ? `$${totalCost}` : 'No data available'}
        </div>
      </div>
    </div>
  );
};

export default Home;
