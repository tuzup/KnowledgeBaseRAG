import React, { useState } from 'react';
import { Grid, Box, Typography } from '@mui/material';
import FileUpload from '../components/FileUpload';
import TaskProgress from '../components/TaskProgress';

const HomePage = () => {
  const [currentTaskId, setCurrentTaskId] = useState(null);

  const handleUploadSuccess = (result) => {
    setCurrentTaskId(result.task_id);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        PDF Document Processing
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload a PDF document to process it with Docling, extract chunks, and enable semantic search.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        </Grid>
        <Grid item xs={12} md={6}>
          {currentTaskId && <TaskProgress taskId={currentTaskId} />}
        </Grid>
      </Grid>
    </Box>
  );
};

export default HomePage;
