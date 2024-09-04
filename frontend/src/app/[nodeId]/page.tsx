"use client"

import { Typography } from "@material-ui/core";
import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { List, ListItem, ListItemText} from '@mui/material';


const NodeComponent = () => {
    const nodeInfo = useSelector((state: RootState) => state.node);
    return (
        <div>
            <List>
                <ListItem>
                    <ListItemText primary={`Name: ${nodeInfo.name}`}/>
                </ListItem>
                <ListItem>
                    <ListItemText primary={`Type: ${nodeInfo.type}`}/>
                </ListItem>
                <ListItem>
                    <ListItemText primary={`Description: ${nodeInfo.description}`}/>
                </ListItem>
            </List>
            {/* <Typography variant="h1">Node Component</Typography> */}
        </div>
    )
}

export default NodeComponent