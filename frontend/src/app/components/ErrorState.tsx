import React from 'react';
import { 
  Box, 
  Paper, 
  Typography,  
  SvgIcon
} from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';


interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({ message }) => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          borderRadius: 2,
          bgcolor: 'background.paper',
          maxWidth: 400,
        }}
      >
        <SvgIcon
          component={ErrorOutlineIcon}
          sx={{ fontSize: 60, color: 'error.main', mb: 2 }}
        />
        <Typography variant="h5" gutterBottom>
          Oops! Something went wrong
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
          {message}
        </Typography>
      </Paper>
    </Box>
  );
};

export default ErrorState;