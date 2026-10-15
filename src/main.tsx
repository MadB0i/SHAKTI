import React from 'react'
import ReactDOM from 'react-dom/client'
import './style.css'
// Separate chunks keep the cultural page independent of Three.js and film loading.
const isDiscover=/\/discover(?:\/|\/index\.html)?$/.test(location.pathname)
const Page=isDiscover?React.lazy(()=>import('./Discover')):React.lazy(()=>import('./App'))
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><React.Suspense fallback={<main className="page-loading" role="status">Preparing SHAKTI…</main>}><Page /></React.Suspense></React.StrictMode>)
