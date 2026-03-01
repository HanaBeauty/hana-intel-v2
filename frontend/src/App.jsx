import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Radar from './pages/Radar';
import ReviewBoard from './pages/ReviewBoard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/radar" replace />} />
          <Route path="radar" element={<Radar />} />
          <Route path="review-board" element={<ReviewBoard />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
