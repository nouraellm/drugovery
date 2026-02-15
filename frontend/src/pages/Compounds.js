import React, { useEffect, useState, useRef } from 'react';
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
  Alert,
  AlertTitle,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
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

  // Import State
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const fileInputRef = useRef(null);



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

  // Import Handlers
  const handleOpenImportDialog = () => {
    setImportDialogOpen(true);
    setImportFile(null);
    setImportResult(null);
  };

  const handleCloseImportDialog = () => {
    setImportDialogOpen(false);
    setImportFile(null);
    setImportResult(null);
  };

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setImportFile(event.target.files[0]);
      setImportResult(null);
    }
  };

  const handleImportSubmit = async () => {
    if (!importFile) return;

    setImporting(true);
    const formData = new FormData();
    formData.append('file', importFile);

    try {
      const response = await compoundsAPI.importFile(formData);
      setImportResult(response.data);
      fetchCompounds(); // Refresh list on success
    } catch (error) {
      console.error('Error importing compounds:', error);
      setImportResult({
        error: error.response?.data?.detail || 'Error importing file',
      });
    } finally {
      setImporting(false);
    }
  };



  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Compounds</Typography>
        <Box>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<CloudUploadIcon />}
            onClick={handleOpenImportDialog}
            sx={{ mr: 2 }}
          >
            Import
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Compound
          </Button>
        </Box>
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

      {/* Add/Edit Dialog */}
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

      {/* Import Dialog */}
      <Dialog
        open={importDialogOpen}
        onClose={handleCloseImportDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Import Compounds</DialogTitle>
        <DialogContent>
          {!importResult && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <input
                accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                style={{ display: 'none' }}
                id="raised-button-file"
                type="file"
                onChange={handleFileChange}
                ref={fileInputRef}
              />
              <label htmlFor="raised-button-file">
                <Button
                  variant="outlined"
                  component="span"
                  startIcon={<CloudUploadIcon />}
                  sx={{ mb: 2 }}
                >
                  Select File (CSV or Excel)
                </Button>
              </label>
              {importFile && (
                <Typography variant="body1" sx={{ mt: 1 }}>
                  Selected: {importFile.name}
                </Typography>
              )}
            </Box>
          )}

          {importing && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, mb: 1 }}>
              <CircularProgress />
            </Box>
          )}

          {importResult && (
            <Box sx={{ mt: 2 }}>
              {importResult.error ? (
                <Alert severity="error">
                  <AlertTitle>Import Failed</AlertTitle>
                  {importResult.error}
                </Alert>
              ) : (
                <Box>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    <AlertTitle>Import Completed</AlertTitle>
                    Successfully imported {importResult.imported} compounds.
                    {importResult.skipped > 0 && ` Skipped ${importResult.skipped} duplicates.`}
                  </Alert>

                  {importResult.errors && importResult.errors.length > 0 && (
                    <Box component={Paper} variant="outlined" sx={{ p: 2, maxHeight: 200, overflow: 'auto' }}>
                      <Typography variant="subtitle2" color="error" gutterBottom>
                        Errors ({importResult.errors.length}):
                      </Typography>
                      <List dense>
                        {importResult.errors.map((err, index) => (
                          <ListItem key={index}>
                            <ListItemText
                              primary={err}
                              primaryTypographyProps={{ variant: 'body2', color: 'error' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseImportDialog}>
            {importResult ? 'Close' : 'Cancel'}
          </Button>
          {!importResult && (
            <Button
              onClick={handleImportSubmit}
              variant="contained"
              disabled={!importFile || importing}
            >
              Import
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
