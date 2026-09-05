import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Shortages from './pages/Shortages';
import MaterialDetail from './pages/MaterialDetail';
import PODetail from './pages/PODetail';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="flex h-screen overflow-hidden bg-slate-900 text-slate-50">
          <Sidebar />
          <main className="flex-1 overflow-y-auto overflow-x-hidden">
            <div className="container mx-auto p-8 max-w-7xl">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/shortages" element={<Shortages />} />
                <Route path="/materials/:id" element={<MaterialDetail />} />
                <Route path="/purchase-orders/:id" element={<PODetail />} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
