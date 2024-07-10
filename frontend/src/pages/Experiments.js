import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';
import { experimentsAPI } from '../services/api';

export default function Experiments() {
  const [experiments, setExperiments] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model_type: 'qsar',
    model_name: '',
  });

  useEffect(() => {
    fetchExperiments();
  }, []);

  const fetchExperiments = async () => {
    try {
      const response = await experimentsAPI.list({ limit: 100 });
      setExperiments(response.data);
    } catch (error) {
      console.error('Error fetching experiments:', error);
    }
  };

  const handleSubmit = async () => {
    try {
      await experimentsAPI.create(formData);
      setDialogOpen(false);
      fetchExperiments();
    } catch (error) {
      console.error('Error creating experiment:', error);
      alert(error.response?.data?.detail || 'Error creating experiment');
    }
  };

  const handleLogToMlflow = async (id) => {
    try {
      await experimentsAPI.logToMlflow(id);
      fetchExperiments();
      alert('Experiment logged to MLflow');
    } catch (error) {
      console.error('Error logging to MLflow:', error);
      alert(error.response?.data?.detail || 'Error logging to MLflow');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      running: 'warning',
      completed: 'success',
      failed: 'error',
    };
    return colors[status] || 'default';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Experiments</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          New Experiment
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Model Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>MLflow Run ID</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {experiments.map((experiment) => (
              <TableRow key={experiment.id}>
                <TableCell>{experiment.id}</TableCell>
                <TableCell>{experiment.name}</TableCell>
                <TableCell>{experiment.model_type}</TableCell>
                <TableCell>
                  <Chip
                    label={experiment.status}
                    color={getStatusColor(experiment.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {experiment.mlflow_run_id || (
                    <IconButton
                      size="small"
                      onClick={() => handleLogToMlflow(experiment.id)}
                      title="Log to MLflow"
                    >
                      <CloudUploadIcon />
                    </IconButton>
                  )}
                </TableCell>
                <TableCell>
                  {new Date(experiment.created_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Experiment</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            margin="normal"
            multiline
            rows={3}
          />
          <TextField
            fullWidth
            label="Model Type"
            value={formData.model_type}
            onChange={(e) =>
              setFormData({ ...formData, model_type: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Model Name"
            value={formData.model_name}
            onChange={(e) =>
              setFormData({ ...formData, model_name: e.target.value })
            }
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
