import React, { useEffect, useState, useCallback } from 'react';
import { usePlaidLink } from 'react-plaid-link';

const Link = ({ onSuccessCallback }) => {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const createLinkToken = async () => {
      const response = await fetch('http://127.0.0.1:8000/create_link_token', {
        method: 'POST',
      });
      const data = await response.json();
      setToken(data.link_token);
    };
    createLinkToken();
  }, []);

  const onSuccess = useCallback(
    async (publicToken) => {
      await fetch('http://127.0.0.1:8000/exchange_public_token?public_token=' + publicToken, {
        method: 'POST',
      });
      // Call the parent callback to refresh data or switch view
      if (onSuccessCallback) onSuccessCallback();
    },
    [onSuccessCallback]
  );

  const { open, ready } = usePlaidLink({
    token,
    onSuccess,
  });

  return (
    <button
        onClick={() => open()}
        disabled={!ready}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition duration-150 ease-in-out disabled:opacity-50"
    >
      Connect Bank Account
    </button>
  );
};

export default Link;
