"use client"

import { useState } from 'react';
import React from 'react';
import axios from "axios";
import styles from './page.module.css';
import { TextField, IconButton, Typography } from "@material-ui/core";
import InputAdornment from "@material-ui/core/InputAdornment";
import SearchIcon from "@material-ui/icons/Search";
import FileUploadIcon from '@mui/icons-material/FileUpload';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import { CircularProgress, VStack, HStack } from "@chakra-ui/react";
import CloseIcon from '@mui/icons-material/Close';
import GraphComponent from './graph/GraphComponent';
import MenuIcon from '@mui/icons-material/Menu';
import { SideMenu } from './components/SideMenu';
import Drawer from '@mui/material/Drawer';
import { getGraphData } from './api/api'
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from "./store/store"



const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState('No file chosen');
  const [fileUploadMessage, setFileUploadMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dispatch = useDispatch<AppDispatch>();
  const graphInfo = useSelector((state: RootState) => state.graph)
  
  const host = "http://localhost:8000"

  const handleMenuToggle = () => {
    setIsMenuOpen(!isMenuOpen);
  };


  const onFileLoad = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files ? event.target.files[0] : null;
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name)
    } else {
      setFileName("No file chosen");
    }
  };

  
  const uploadFile = () => {
    setUploading(true);
    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      axios.post(host + "/uploadParagraph", formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then(response => {
        console.log('Success:', response.data);
        // Handle response here
        setFileUploadMessage("Successfully uploaded")
        setUploading(false);
      })
      .catch(error => {
        console.log('Error:', error);
        setUploading(false);
        console.log(error.response.data.error);
        setFileUploadMessage(error.response.data.error);
        // Handle errors here
      });
    }
  };

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    dispatch(getGraphData(searchQuery));
  }
 

  return (
    <div className = {styles["page-container"]}>
        <IconButton 
            className={styles["menu-icon"]}
            edge="start" 
            color="inherit" 
            aria-label="menu" 
            onClick={handleMenuToggle}
        >
            <MenuIcon />
        </IconButton>
        <Drawer open={isMenuOpen} onClose={handleMenuToggle}>
          {SideMenu}
        </Drawer>
        <div className={styles["header-container"]}>
            <Typography variant="h2">
            Welcome to the Current Events Tracker!
            </Typography>
            <Typography variant="h4">
                Ask a question to get started
            </Typography>
        </div>
        
      <VStack>
      <div className={styles["search-form"]}>
          <form onSubmit={handleSearchSubmit}>
            <TextField
              label="Search"
              fullWidth
              value={searchQuery}
              onChange={(e)=>setSearchQuery(e.target.value)}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="start">
                    <IconButton type="submit">
                      <SearchIcon />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
          </form>
        </div>
        <Typography className={styles["search-answer"]}>{graphInfo.answer}</Typography>
        {/* {graphData.length > 0 && entityData && (
          <div style={{ width: '100%', height: '400px' }}>
            <GraphComponent metadata={graphData} entityData={entityData} />
          </div>)} */}
        {graphInfo.graphData.length > 0 && graphInfo.entityData && (
          <div className={styles.graphContainer}>
            <div className={styles.graphWrapper}>
              <GraphComponent metadata={graphInfo.graphData} entityData={graphInfo.entityData} />
            </div>
          </div>
        )}
      
        <Typography className={styles["or"]} variant="h2">or</Typography>
        <div className={styles["file-uploader"]}>
          <HStack>
          <input 
                type="file" 
                accept=".pdf" 
                onChange={onFileLoad} 
                style={{ display: 'none' }} 
                id={styles["file-input"]}
            />
            <label htmlFor="file-input" className={styles['file-label']}>
              <AttachFileIcon className={styles["attach-icon"]}/>
              Choose a File to Upload
            </label>
            <span className={styles["file-name"]}>{fileName}</span>
          {file && 
          <IconButton 
              onClick={()=>setFile(null)}
              color="primary">
              <CloseIcon />
          </IconButton>
          }
          </HStack>
        </div>
        <div className={styles["mb-4"]}>
          {uploading ?         
            // <CircularProgress size={100} strokeWidth={10} percentage={75}/> :
            // <button onClick={uploadFile} disabled={!file}>Upload PDF</button>
            <CircularProgress 
              display="flex" alignItems="center" 
              isIndeterminate  size="128px" thickness='2px'
              color="var(--foreground-foundations-fg-default, #202427)">
              </CircularProgress>:
            <IconButton 
              onClick={uploadFile} 
              disabled={!file} 
              aria-label="upload pdf"
              color="primary">
              <FileUploadIcon />
              Upload File
          </IconButton>
          }
        </div>
        <div>{fileUploadMessage}</div>
      </VStack>
    </div>
  );
};

export default App;
