import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Cacher le loading spinner
setTimeout(() => {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}, 1000);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
