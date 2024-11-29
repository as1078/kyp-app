"use client"

import { useEffect, useState } from 'react';
import { loadImageFromUrl } from '../api/api';
import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { List, ListItem, ListItemText, Box } from '@mui/material';
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";


const NodeComponent = () => {
    const { entity, image, status, error } = useSelector((state: RootState) => state.node);
    const [loadedImage, setLoadedImage] = useState<string | null>(null);
    console.log("entity: " + entity );
    console.log("image: " + image );
    console.log("status: " + status);
    
    useEffect(() => {
        if (image.url) {
            loadImageFromUrl(image.url)
                .then(setLoadedImage)
                .catch(console.error);
        }
      }, [image.url]);
    if (status === 'loading') {
        return <LoadingState/>
    }
    else if (status == 'succeeded' || status == 'cypher_succeeded') {
        return (
            <div>
                <List>
                    <ListItem>
                        <ListItemText primary={`Name: ${entity.name}`}/>
                    </ListItem>
                    <ListItem>
                        <ListItemText primary={`Type: ${entity.type}`}/>
                    </ListItem>
                    <ListItem>
                        <ListItemText primary={`Description: ${entity.description}`}/>
                    </ListItem>
                </List>
                {loadedImage && <Box
                    component="img"
                    sx={{
                        height: 300,
                        width: 400,
                        maxHeight: { xs: 233, md: 167 },
                        maxWidth: { xs: 350, md: 250 },
                    }}
                    src={loadedImage}       
                />}
            </div>
        )
    }
    else if (status === 'failed') {
        return <ErrorState message={`Failed to load data for node". ${error}`}/>
    }

}

export default NodeComponent