import React, { useEffect, useState } from 'react';
import {
    Card, CardContent, Typography, CircularProgress, Chip,
    Grid, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Button
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
                    <Grid item xs={12} sm={6} md={4} key={index}>
                        <Card raised onClick={() => handleClickOpen(market)} style={{ cursor: 'pointer' }}>
                            <CardContent>
                                <Typography variant="h6">{market.name}</Typography>
                                <Typography>Protocol: {market.protocol}</Typography>
                                <Typography>Version: {market.version}</Typography>
                                <Chip label={`Contract Address: ${market.contract_address}`} color="primary" />
                                <Typography>Creation Date: {market.create_dt}</Typography>
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
                            Name: {selectedMarketplace.name}<br />
                            Protocol: {selectedMarketplace.protocol}<br />
                            Version: {selectedMarketplace.version}<br />
                            Contract Address: {selectedMarketplace.contract_address}<br />
                            Creation Date: {selectedMarketplace.create_dt}
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
