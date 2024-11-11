"use client"

import { Typography } from "@material-ui/core";
import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { List, ListItem, ListItemText} from '@mui/material';
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";

const NodeComponent = () => {
    const { nodes, status, error } = useSelector((state: RootState) => state.node);
    if (status === 'loading') {
        return <LoadingState/>
    }
    else if (status == 'succeeded') {
        return (
            <div>
                {nodes?.map((nodeInfo, index) => (
                    <List key={index}>
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
                ))}
            </div>
        )
    }
    else if (status === 'failed') {
        return <ErrorState message={`Failed to load data for node". ${error}`}/>
    }

}

export default NodeComponent