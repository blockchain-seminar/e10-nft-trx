import React, { useEffect, useState } from 'react';
import {
    Card, CardContent, Typography, CircularProgress, Chip,
    Grid, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button, Divider
} from '@mui/material';

function Marketplaces() {
    const [marketplaces, setMarketplaces] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedMarketplace, setSelectedMarketplace] = useState(null);
    const [open, setOpen] = useState(false);

    const handleClickOpen = (market) => {
        setSelectedMarketplace(market);
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    useEffect(() => {
        fetch('http://127.0.0.1:5000/marketplaces')
            .then(response => response.json())
            .then(data => {
                setMarketplaces(data);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching marketplaces:', error);
                setLoading(false);
            });
    }, []);

    if (loading) return <CircularProgress />;

    return (
        <div style={{ padding: 20 }}>
            <Typography variant="h4" gutterBottom>
                Marketplaces
            </Typography>
            <Grid container spacing={3}>
                {marketplaces.map((market, index) => (
                    <Grid item xs={12} sm={6} md={6} key={index}>
                        <Card raised onClick={() => handleClickOpen(market)} style={{ cursor: 'pointer' }}>
                            <CardContent>
                                <Grid container spacing={2} alignItems="center">
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Market Name:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {market.name}
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Market Protocol:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {market.protocol}
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Market Version:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {market.version}
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Contract Address:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Chip label={`${market.contract_address}`} variant="outlined" color="success" />
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Creation Date:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {market.create_dt}
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            {selectedMarketplace && (
                <Dialog open={open} onClose={handleClose}>
                    <DialogTitle>{"Marketplace Details"}</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            <Grid container spacing={2} alignItems="center">
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>Market Name:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    {selectedMarketplace.name}
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>Market Protocol:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    {selectedMarketplace.protocol}
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>Market Version:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    {selectedMarketplace.version}
                                </Grid>
                                <Divider sx={{my: 1, width: '100%'}}/>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>Contract Address:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={`${selectedMarketplace.contract_address}`} variant="outlined" color="success" />
                                </Grid>
                                <Divider sx={{my: 1, width: '100%'}}/>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{fontWeight: 'bold'}}>Creation Date:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    {selectedMarketplace.create_dt}
                                </Grid>
                                <Divider sx={{my: 1, width: '100%'}}/>
                            </Grid>
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose} color="primary">
                            Close
                        </Button>
                    </DialogActions>
                </Dialog>
            )}
        </div>
    );
}

export default Marketplaces;
