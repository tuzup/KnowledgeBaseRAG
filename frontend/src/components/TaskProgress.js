import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Alert,
  Chip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import { getTaskStatus } from '../services/api';

const TaskProgress = ({ taskId }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!taskId) return;

    const pollStatus = async () => {
      try {
        const result = await getTaskStatus(taskId);
        setStatus(result);
        setLoading(false);

        // Continue polling if task is not finished
        if (result.status === 'PENDING' || result.status === 'STARTED') {
          setTimeout(pollStatus, 2000);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch status');
        setLoading(false);
      }
    };

    pollStatus();
  }, [taskId]);

  if (!taskId) return null;

  const getStatusIcon = () => {
    if (!status) return null;
    switch (status.status) {
      case 'SUCCESS':
        return <CheckCircleIcon color="success" />;
      case 'FAILURE':
        return <ErrorIcon color="error" />;
      default:
        return <HourglassEmptyIcon color="action" />;
    }
  };

  const getStatusColor = () => {
    if (!status) return 'default';
    switch (status.status) {
      case 'SUCCESS':
        return 'success';
      case 'FAILURE':
        return 'error';
      case 'STARTED':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Processing Status
      </Typography>

      <Box sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          {getStatusIcon()}
          <Chip 
            label={status?.status || 'LOADING'} 
            color={getStatusColor()}
            size="small"
          />
        </Box>

        {(loading || status?.status === 'PENDING' || status?.status === 'STARTED') && (
          <LinearProgress sx={{ mb: 2 }} />
        )}

        {status?.progress && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Stage: {status.progress.stage} ({status.progress.progress}%)
          </Typography>
        )}

        {status?.result && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              Processed {status.result.chunks_processed} chunks
            </Typography>
            <Typography variant="body2">
              Document ID: {status.result.document_id}
            </Typography>
          </Alert>
        )}

        {status?.error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {status.error}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Box>
    </Paper>
  );
};

export default TaskProgress;
