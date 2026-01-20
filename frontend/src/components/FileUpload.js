import React, { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  LinearProgress,
  Alert,
  TextField,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadFile, processDocument } from '../services/api';

const FileUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a PDF file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }
    if (!category) {
      setError('Please enter a category');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      // Upload file
      const uploadResult = await uploadFile(file);

      // Process document
      const processResult = await processDocument(
        uploadResult.file_path,
        category,
        subcategory
      );

      setSuccess(`File uploaded successfully! Task ID: ${processResult.task_id}`);

      if (onUploadSuccess) {
        onUploadSuccess(processResult);
      }

      // Reset form
      setFile(null);
      setCategory('');
      setSubcategory('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload PDF Document
      </Typography>

      <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <input
          accept="application/pdf"
          style={{ display: 'none' }}
          id="raised-button-file"
          type="file"
          onChange={handleFileChange}
        />
        <label htmlFor="raised-button-file">
          <Button
            variant="outlined"
            component="span"
            startIcon={<CloudUploadIcon />}
            fullWidth
          >
            Choose PDF File
          </Button>
        </label>

        {file && (
          <Typography variant="body2" color="text.secondary">
            Selected: {file.name}
          </Typography>
        )}

        <TextField
          label="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          fullWidth
          required
        />

        <TextField
          label="Subcategory (Optional)"
          value={subcategory}
          onChange={(e) => setSubcategory(e.target.value)}
          fullWidth
        />

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || !category || uploading}
          fullWidth
        >
          {uploading ? 'Uploading...' : 'Upload and Process'}
        </Button>

        {uploading && <LinearProgress />}

        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">{success}</Alert>}
      </Box>
    </Paper>
  );
};

export default FileUpload;
