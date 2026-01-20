import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ChunksPage from './pages/ChunksPage';
import SearchPage from './pages/SearchPage';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chunks" element={<ChunksPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;
