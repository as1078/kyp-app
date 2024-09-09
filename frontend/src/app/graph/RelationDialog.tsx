import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@material-ui/core";
import { useState, useEffect } from "react";
import { EdgeData } from "./GraphData";
import { FullItem } from "vis-data/declarations/data-interface";

interface RelationDialogProps {
    edge: FullItem<EdgeData, "id">;
    onClose: () => void;
  }

const RelationDialog: React.FC<RelationDialogProps> = ({ edge, onClose }) => {
    useEffect(() => {
      console.log("Open state value: " + open);
    }, []);
    const [open, setOpen] = useState(true);
    const handleClose = () => {
      onClose();
      setOpen(false);
    }
    return (
      <>
        <Dialog 
          open={open} 
          onClose={handleClose}
          aria-labelledby="dialog-title"
          aria-describedby="dialog-description"
        >
          <DialogTitle id="dialog-title">Dialog Title</DialogTitle>
          <DialogContent>
            {edge.description}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Close</Button>
          </DialogActions>
        </Dialog>
      </>
    );
  }

export default RelationDialog