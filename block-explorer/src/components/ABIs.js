import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, CircularProgress, Chip, Grid, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Card)({
    '&:hover': {
        cursor: 'pointer',
        boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
    },
});

function ABIs() {
    const [abis, setABIs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [selectedABI, setSelectedABI] = useState(null);

    const handleClickOpen = (abi) => {
        setSelectedABI(abi);
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    useEffect(() => {
        fetch('http://127.0.0.1:5000/abis')
            .then(response => response.json())
            .then(data => {
                setABIs(data);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching ABIs:', error);
                setLoading(false);
            });
    }, []);

    if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center' }}><CircularProgress /></Box>;

    return (
        <Box sx={{ flexGrow: 1, padding: 3 }}>
            <Typography variant="h4" gutterBottom component="div">
                ABI Events
            </Typography>
            <Grid container spacing={3}>
                {abis.map((abi, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                        <StyledCard raised onClick={() => handleClickOpen(abi)}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    {abi.name}
                                </Typography>
                                <Typography variant="subtitle1" color="text.secondary">
                                    Type: {abi.type}
                                </Typography>
                                <Chip label={`Address: ${abi.contract_address}`} color="primary" />
                            </CardContent>
                        </StyledCard>
                    </Grid>
                ))}
            </Grid>
            {selectedABI && (
                <Dialog open={open} onClose={handleClose} aria-labelledby="dialog-title" aria-describedby="dialog-description">
                    <DialogTitle id="dialog-title">{"ABI Event Details"}</DialogTitle>
                    <DialogContent>
                        <DialogContentText id="dialog-description">
                            Name: {selectedABI.name}<br/>
                            Type: {selectedABI.type}<br/>
                            Contract Address: {selectedABI.contract_address}
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose} color="primary" autoFocus>
                            Close
                        </Button>
                    </DialogActions>
                </Dialog>
            )}
        </Box>
    );
}

export default ABIs;
