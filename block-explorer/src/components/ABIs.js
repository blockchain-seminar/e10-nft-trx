import React, { useEffect, useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Chip,
    Grid,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    Button,
    Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {Link as RouterLink} from "react-router-dom";

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
                                <Grid container spacing={2} alignItems="center">
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>ABI:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {abi.name}
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Type:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {abi.type}
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>

                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Address:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Chip label={`Address: ${abi.contract_address}`} variant="outlined" color="success" />
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                </Grid>
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
                            <Grid container spacing={2} alignItems="center">
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>ABI:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    {selectedABI.name}
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>Type:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    {selectedABI.type}
                                </Grid>
                                <Divider sx={{my: 1, width: '100%'}}/>

                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>Address:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={`Address: ${selectedABI.contract_address}`} variant="outlined" color="success" />
                                </Grid>
                                <Divider sx={{my: 1, width: '100%'}}/>
                            </Grid>
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
