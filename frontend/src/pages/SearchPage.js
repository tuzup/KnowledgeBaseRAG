import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Slider,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { searchDocuments } from '../services/api';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searched, setSearched] = useState(false);

  // Filters
  const [nResults, setNResults] = useState(10);
  const [imagesOnly, setImagesOnly] = useState(false);
  const [tablesOnly, setTablesOnly] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setSearched(true);

    try {
      const result = await searchDocuments(query, nResults, {
        images_only: imagesOnly,
        tables_only: tablesOnly,
      });
      setResults(result.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Semantic Search
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Search through processed document chunks using semantic similarity.
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Search Query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter your search query..."
              variant="outlined"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography gutterBottom>
              Number of Results: {nResults}
            </Typography>
            <Slider
              value={nResults}
              onChange={(e, newValue) => setNResults(newValue)}
              min={1}
              max={50}
              valueLabelDisplay="auto"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormGroup row>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={imagesOnly}
                    onChange={(e) => setImagesOnly(e.target.checked)}
                  />
                }
                label="Images Only"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={tablesOnly}
                    onChange={(e) => setTablesOnly(e.target.checked)}
                  />
                }
                label="Tables Only"
              />
            </FormGroup>
          </Grid>

          <Grid item xs={12}>
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              fullWidth
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {searched && !loading && results.length === 0 && (
        <Alert severity="info">No results found. Try a different query.</Alert>
      )}

      <Grid container spacing={2}>
        {results.map((result, index) => (
          <Grid item xs={12} key={result.chunk_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  <Chip label={`Result ${index + 1}`} size="small" color="primary" />
                  <Chip label={`Distance: ${result.distance.toFixed(3)}`} size="small" />
                  <Chip label={result.metadata.category} size="small" />
                  {result.metadata.page_numbers && (
                    <Chip label={`Pages: ${result.metadata.page_numbers}`} size="small" />
                  )}
                  {result.metadata.has_images && (
                    <Chip label={`Images: ${result.metadata.image_count}`} size="small" color="secondary" />
                  )}
                  {result.metadata.table_count > 0 && (
                    <Chip label={`Tables: ${result.metadata.table_count}`} size="small" color="secondary" />
                  )}
                </Box>

                {result.metadata.title && (
                  <Typography variant="h6" gutterBottom>
                    {result.metadata.title}
                  </Typography>
                )}

                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
                  {result.document_text}
                </Typography>

                <Typography variant="caption" color="text.secondary">
                  Source: {result.metadata.filename}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default SearchPage;
