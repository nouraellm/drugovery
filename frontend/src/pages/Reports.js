import React, { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  Description as DescriptionIcon,
  GetApp as GetAppIcon,
} from '@mui/icons-material';
import { reportsAPI } from '../services/api';

export default function Reports() {
  const [loading, setLoading] = useState('');

  const handleExport = async (type, params = {}) => {
    setLoading(type);
    try {
      let response;
      if (type === 'compounds-csv') {
        response = await reportsAPI.exportCompoundsCSV(params);
      } else if (type === 'predictions-csv') {
        response = await reportsAPI.exportPredictionsCSV(params);
      } else if (type.startsWith('experiment-pdf-')) {
        const experimentId = type.split('-').pop();
        response = await reportsAPI.exportExperimentPDF(experimentId);
      }

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename =
        type === 'compounds-csv'
          ? 'compounds.csv'
          : type === 'predictions-csv'
          ? 'predictions.csv'
          : `experiment_${type.split('-').pop()}_report.pdf`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting report:', error);
      alert('Error exporting report');
    } finally {
      setLoading('');
    }
  };

  const ReportCard = ({ title, description, onExport, exportType }) => (
    <Card>
      <CardContent>
        <DescriptionIcon sx={{ fontSize: 40, mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          size="small"
          startIcon={<GetAppIcon />}
          onClick={() => onExport(exportType)}
          disabled={loading === exportType}
        >
          {loading === exportType ? 'Exporting...' : 'Export'}
        </Button>
      </CardActions>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Generate and export reports in various formats
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <ReportCard
            title="Compounds CSV"
            description="Export all compounds to CSV format"
            onExport={handleExport}
            exportType="compounds-csv"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <ReportCard
            title="Predictions CSV"
            description="Export all predictions to CSV format"
            onExport={handleExport}
            exportType="predictions-csv"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Experiment PDF Report
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Generate PDF report for a specific experiment
            </Typography>
            <Button
              variant="outlined"
              startIcon={<GetAppIcon />}
              onClick={() => {
                const experimentId = prompt('Enter Experiment ID:');
                if (experimentId) {
                  handleExport(`experiment-pdf-${experimentId}`);
                }
              }}
            >
              Generate PDF
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
