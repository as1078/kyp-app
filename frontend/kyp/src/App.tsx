import { useState } from 'react';
import './App.css';
import axios from "axios";
import { TextField, IconButton, Typography } from "@material-ui/core";
import InputAdornment from "@material-ui/core/InputAdornment";
import SearchIcon from "@material-ui/icons/Search";
import FileUploadIcon from '@mui/icons-material/FileUpload';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import { CircularProgress, VStack, HStack } from "@chakra-ui/react";
import CloseIcon from '@mui/icons-material/Close';
import GraphComponent from './graph/GraphComponent';
import { RelationshipMetadata, NodeData } from './graph/GraphData';


const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState('No file chosen');
  const [fileUploadMessage, setFileUploadMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState('');
  const [searchAnswer, setSearchAnswer] = useState('');
  const [graphData, setGraphData] = useState<RelationshipMetadata[]>([]);
  const [entityData, setEntityData] = useState<NodeData>();
  const [uploading, setUploading] = useState(false);
  const host = "http://localhost:8000"
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
    handleSearch();
  }

  async function handleSearch () {
    await axios.get(host + `/search?query=${searchQuery}`)
      .then(res => {
        if (res.status === 200) {
          console.log(res)
          setSearchAnswer(res.data.answer)
          const metadata = res.data.metadata
          const entityData = metadata.EntityData
          console.log(entityData)
          const relationshipsData = metadata.RelationshipsData
          const parsedMetadata: RelationshipMetadata[] = relationshipsData.map((item: any) => ({
            descriptionText: item.descriptionText,
            entityName1: item.entityName1,
            entityName2: item.entityName2,
            type: item.type
          }));
          const firstEntity = entityData[0]
          const parsedEntityData = new NodeData("1", firstEntity.name)
          setEntityData(parsedEntityData);
          setGraphData(parsedMetadata)
          console.log(parsedMetadata)
        } else {
          console.error("Unexpected status code:", res.status);
        }
      }).catch(error => {
        console.error("Axios request error:", error);
    })
  }
 

  return (
    <>
      <h1>
        Welcome to Know Your Politician!
      </h1>
      <h2>Ask a question to get started</h2>
      <VStack>
      <div className="mb-4">
          <form onSubmit={handleSearchSubmit} className="search">
          <TextField
            label="Search"
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
        <Typography>{searchAnswer}</Typography>
        {graphData.length > 0 && entityData && (
          <div style={{ width: '100%', height: '400px' }}>
            <GraphComponent metadata={graphData} entityData={entityData} />
          </div>)}
        
        {/* <Typography>{graphData}</Typography> */}
        <h1>or</h1>
        <div className="file-uploader">
          <HStack>
          <input 
                type="file" 
                accept=".pdf" 
                onChange={onFileLoad} 
                style={{ display: 'none' }} 
                id="file-input" 
            />
            <label htmlFor="file-input" className="file-label">
              <AttachFileIcon className="attach-icon"/>
              Choose a File to Upload
            </label>
            <span className="file-name">{fileName}</span>
          {file && 
          <IconButton 
              onClick={()=>setFile(null)}
              color="primary">
              <CloseIcon />
          </IconButton>
          }
          </HStack>
        </div>
        <div className="mb-4">
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
    </>
  );
};

export default App;
