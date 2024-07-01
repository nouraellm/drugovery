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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
} from '@mui/material';
import { Psychology as PsychologyIcon } from '@mui/icons-material';
import { predictionsAPI, compoundsAPI } from '../services/api';

export default function Predictions() {
  const [predictions, setPredictions] = useState([]);
  const [compounds, setCompounds] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [batchDialogOpen, setBatchDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    compound_id: '',
    model_type: 'solubility',
    model_name: '',
  });
  const [batchFormData, setBatchFormData] = useState({
    compound_ids: [],
    model_type: 'solubility',
    model_name: '',
  });

  useEffect(() => {
    fetchPredictions();
    fetchCompounds();
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await predictionsAPI.list({ limit: 100 });
      setPredictions(response.data);
    } catch (error) {
      console.error('Error fetching predictions:', error);
    }
  };

  const fetchCompounds = async () => {
    try {
      const response = await compoundsAPI.list({ limit: 1000 });
      setCompounds(response.data);
    } catch (error) {
      console.error('Error fetching compounds:', error);
    }
  };

  const handleSubmit = async () => {
    try {
      await predictionsAPI.create(formData);
      setDialogOpen(false);
      fetchPredictions();
    } catch (error) {
      console.error('Error creating prediction:', error);
      alert(error.response?.data?.detail || 'Error creating prediction');
    }
  };

  const handleBatchSubmit = async () => {
    try {
      await predictionsAPI.batch(batchFormData);
      setBatchDialogOpen(false);
      alert('Batch prediction task queued');
      setTimeout(fetchPredictions, 2000);
    } catch (error) {
      console.error('Error creating batch prediction:', error);
      alert(error.response?.data?.detail || 'Error creating batch prediction');
    }
  };

  const getModelTypeColor = (type) => {
    const colors = {
      solubility: 'primary',
      toxicity: 'error',
      dti: 'secondary',
    };
    return colors[type] || 'default';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Predictions</Typography>
        <Box>
          <Button
            variant="outlined"
            sx={{ mr: 2 }}
            onClick={() => setBatchDialogOpen(true)}
          >
            Batch Prediction
          </Button>
          <Button
            variant="contained"
            startIcon={<PsychologyIcon />}
            onClick={() => setDialogOpen(true)}
          >
            New Prediction
          </Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Compound ID</TableCell>
              <TableCell>Model Type</TableCell>
              <TableCell>Model Name</TableCell>
              <TableCell>Prediction Value</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell>Created At</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {predictions.map((prediction) => (
              <TableRow key={prediction.id}>
                <TableCell>{prediction.id}</TableCell>
                <TableCell>{prediction.compound_id}</TableCell>
                <TableCell>
                  <Chip
                    label={prediction.model_type}
                    color={getModelTypeColor(prediction.model_type)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{prediction.model_name || '-'}</TableCell>
                <TableCell>
                  {prediction.prediction_value
                    ? prediction.prediction_value.toFixed(4)
                    : '-'}
                </TableCell>
                <TableCell>
                  {prediction.prediction_confidence
                    ? (prediction.prediction_confidence * 100).toFixed(1) + '%'
                    : '-'}
                </TableCell>
                <TableCell>
                  {new Date(prediction.created_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Prediction</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Compound</InputLabel>
            <Select
              value={formData.compound_id}
              onChange={(e) =>
                setFormData({ ...formData, compound_id: e.target.value })
              }
            >
              {compounds.map((compound) => (
                <MenuItem key={compound.id} value={compound.id}>
                  {compound.name} ({compound.smiles})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Model Type</InputLabel>
            <Select
              value={formData.model_type}
              onChange={(e) =>
                setFormData({ ...formData, model_type: e.target.value })
              }
            >
              <MenuItem value="solubility">Solubility</MenuItem>
              <MenuItem value="toxicity">Toxicity</MenuItem>
              <MenuItem value="dti">Drug-Target Interaction</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Model Name (optional)"
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

      <Dialog
        open={batchDialogOpen}
        onClose={() => setBatchDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Batch Prediction</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Compounds (select multiple)</InputLabel>
            <Select
              multiple
              value={batchFormData.compound_ids}
              onChange={(e) =>
                setBatchFormData({
                  ...batchFormData,
                  compound_ids: e.target.value,
                })
              }
            >
              {compounds.map((compound) => (
                <MenuItem key={compound.id} value={compound.id}>
                  {compound.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Model Type</InputLabel>
            <Select
              value={batchFormData.model_type}
              onChange={(e) =>
                setBatchFormData({ ...batchFormData, model_type: e.target.value })
              }
            >
              <MenuItem value="solubility">Solubility</MenuItem>
              <MenuItem value="toxicity">Toxicity</MenuItem>
              <MenuItem value="dti">Drug-Target Interaction</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBatchDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleBatchSubmit} variant="contained">
            Queue Batch
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
