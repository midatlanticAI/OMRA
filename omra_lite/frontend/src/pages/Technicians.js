import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const Technicians = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Technicians
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          This page will display the list of technicians and allow you to manage them.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Technicians; 