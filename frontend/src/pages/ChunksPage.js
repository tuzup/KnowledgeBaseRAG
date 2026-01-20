import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination,
} from '@mui/material';
import { listChunks, listDocuments } from '../services/api';

const ChunksPage = () => {
  const [chunks, setChunks] = useState([]);
  const [documents, setDocuments] = useState({});
  const [selectedDoc, setSelectedDoc] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const chunksPerPage = 10;

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    loadChunks();
  }, [selectedDoc, page]);

  const loadDocuments = async () => {
    try {
      const result = await listDocuments();
      setDocuments(result.documents);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const loadChunks = async () => {
    setLoading(true);
    setError(null);
    try {
      const offset = (page - 1) * chunksPerPage;
      const result = await listChunks(selectedDoc || null, chunksPerPage, offset);
      setChunks(result.chunks);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load chunks');
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentChange = (event) => {
    setSelectedDoc(event.target.value);
    setPage(1);
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const totalPages = Math.ceil(chunks.length / chunksPerPage);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Document Chunks
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <FormControl fullWidth>
          <InputLabel>Filter by Document</InputLabel>
          <Select
            value={selectedDoc}
            onChange={handleDocumentChange}
            label="Filter by Document"
          >
            <MenuItem value="">All Documents</MenuItem>
            {Object.entries(documents).map(([docId, doc]) => (
              <MenuItem key={docId} value={docId}>
                {doc.filename} ({doc.category})
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Paper>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {!loading && chunks.length === 0 && (
        <Alert severity="info">No chunks found. Upload a document first.</Alert>
      )}

      <Grid container spacing={2}>
        {chunks.map((chunk, index) => (
          <Grid item xs={12} key={chunk.chunk_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  <Chip label={`Chunk ${index + 1}`} size="small" color="primary" />
                  <Chip label={chunk.metadata.category} size="small" />
                  {chunk.metadata.page_numbers && (
                    <Chip label={`Pages: ${chunk.metadata.page_numbers}`} size="small" />
                  )}
                  {chunk.metadata.has_images && (
                    <Chip label={`Images: ${chunk.metadata.image_count}`} size="small" color="secondary" />
                  )}
                  {chunk.metadata.table_count > 0 && (
                    <Chip label={`Tables: ${chunk.metadata.table_count}`} size="small" color="secondary" />
                  )}
                </Box>

                {chunk.metadata.title && (
                  <Typography variant="h6" gutterBottom>
                    {chunk.metadata.title}
                  </Typography>
                )}

                <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                  {chunk.text.substring(0, 500)}
                  {chunk.text.length > 500 && '...'}
                </Typography>

                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Document: {chunk.metadata.filename}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {chunks.length > 0 && totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination 
            count={totalPages} 
            page={page} 
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
};

export default ChunksPage;
