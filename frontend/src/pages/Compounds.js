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
  TextField,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { compoundsAPI } from '../services/api';

export default function Compounds() {
  const [compounds, setCompounds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCompound, setEditingCompound] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    smiles: '',
    molecular_formula: '',
    molecular_weight: '',
  });

  useEffect(() => {
    fetchCompounds();
  }, [search]);

  const fetchCompounds = async () => {
    setLoading(true);
    try {
      const response = await compoundsAPI.list({ search, limit: 100 });
      setCompounds(response.data);
    } catch (error) {
      console.error('Error fetching compounds:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (compound = null) => {
    if (compound) {
      setEditingCompound(compound);
      setFormData({
        name: compound.name,
        smiles: compound.smiles,
        molecular_formula: compound.molecular_formula || '',
        molecular_weight: compound.molecular_weight || '',
      });
    } else {
      setEditingCompound(null);
      setFormData({
        name: '',
        smiles: '',
        molecular_formula: '',
        molecular_weight: '',
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingCompound(null);
  };

  const handleSubmit = async () => {
    try {
      if (editingCompound) {
        await compoundsAPI.update(editingCompound.id, formData);
      } else {
        await compoundsAPI.create(formData);
      }
      handleCloseDialog();
      fetchCompounds();
    } catch (error) {
      console.error('Error saving compound:', error);
      alert(error.response?.data?.detail || 'Error saving compound');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this compound?')) {
      try {
        await compoundsAPI.delete(id);
        fetchCompounds();
      } catch (error) {
        console.error('Error deleting compound:', error);
        alert(error.response?.data?.detail || 'Error deleting compound');
      }
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Compounds</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Compound
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <TextField
          fullWidth
          label="Search compounds"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name, SMILES, or formula..."
        />
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>SMILES</TableCell>
              <TableCell>Molecular Formula</TableCell>
              <TableCell>Molecular Weight</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {compounds.map((compound) => (
              <TableRow key={compound.id}>
                <TableCell>{compound.id}</TableCell>
                <TableCell>{compound.name}</TableCell>
                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  {compound.smiles}
                </TableCell>
                <TableCell>{compound.molecular_formula || '-'}</TableCell>
                <TableCell>
                  {compound.molecular_weight
                    ? compound.molecular_weight.toFixed(2)
                    : '-'}
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog(compound)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(compound.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingCompound ? 'Edit Compound' : 'Add Compound'}
        </DialogTitle>
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
            label="SMILES"
            value={formData.smiles}
            onChange={(e) => setFormData({ ...formData, smiles: e.target.value })}
            margin="normal"
            required
            helperText="Enter SMILES notation (e.g., CCO for ethanol)"
          />
          <TextField
            fullWidth
            label="Molecular Formula"
            value={formData.molecular_formula}
            onChange={(e) =>
              setFormData({ ...formData, molecular_formula: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Molecular Weight"
            type="number"
            value={formData.molecular_weight}
            onChange={(e) =>
              setFormData({ ...formData, molecular_weight: e.target.value })
            }
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingCompound ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
