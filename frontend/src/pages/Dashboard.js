import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  Science as ScienceIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { compoundsAPI, predictionsAPI, experimentsAPI } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    compounds: 0,
    predictions: 0,
    experiments: 0,
  });
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  const fetchStats = async () => {
    setLoading(true);
    try {
      // Fetch all items to get accurate counts (with reasonable limits)
      const [compounds, predictions, experiments] = await Promise.all([
        compoundsAPI.list({ limit: 1000 }),
        predictionsAPI.list({ limit: 1000 }),
        experimentsAPI.list({ limit: 1000 }),
      ]);
      setStats({
        compounds: compounds.data?.length || 0,
        predictions: predictions.data?.length || 0,
        experiments: experiments.data?.length || 0,
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
      // Set to 0 on error to show something
      setStats({
        compounds: 0,
        predictions: 0,
        experiments: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [location.pathname]); // Refresh when navigating to dashboard

  const StatCard = ({ title, value, icon, color }) => (
    <Paper
      sx={{
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        backgroundColor: color || 'primary.main',
        color: 'white',
      }}
    >
      {icon}
      <Typography variant="h4" sx={{ mt: 2 }}>
        {value}
      </Typography>
      <Typography variant="h6" sx={{ mt: 1 }}>
        {title}
      </Typography>
    </Paper>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={4}>
          <StatCard
            title="Compounds"
            value={stats.compounds}
            icon={<ScienceIcon sx={{ fontSize: 60 }} />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            title="Predictions"
            value={stats.predictions}
            icon={<PsychologyIcon sx={{ fontSize: 60 }} />}
            color="secondary.main"
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <StatCard
            title="Experiments"
            value={stats.experiments}
            icon={<AssessmentIcon sx={{ fontSize: 60 }} />}
            color="success.main"
          />
        </Grid>
      </Grid>
    </Box>
  );
}
