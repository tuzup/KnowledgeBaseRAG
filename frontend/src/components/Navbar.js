import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SearchIcon from '@mui/icons-material/Search';
import ArticleIcon from '@mui/icons-material/Article';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Docling PDF Processor
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            color="inherit"
            component={RouterLink}
            to="/"
            startIcon={<UploadFileIcon />}
          >
            Upload
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/chunks"
            startIcon={<ArticleIcon />}
          >
            Chunks
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/search"
            startIcon={<SearchIcon />}
          >
            Search
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
