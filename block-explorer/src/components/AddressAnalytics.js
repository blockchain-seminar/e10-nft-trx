import React, { useState, useEffect } from 'react';
import {
    Typography,
    Card,
    CardContent,
    Chip,
    Grid,
    CircularProgress,
    Dialog,
    Pagination,
    DialogTitle,
    DialogContent,
    Button,
    Divider,
    DialogActions
} from '@mui/material';
import {Link, useParams} from 'react-router-dom';

function AddressAnalytics() {
    const { address } = useParams();
    const [priceData, setPriceData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedData, setSelectedData] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [searchedAddress, setSearchedAddress] = useState('');

    useEffect(() => {
        if (address) {  // Ensure there is an address before fetching
            fetch(`http://127.0.0.1:5000/analytics/price_data_by_address?address=${address}&page=${page}&per_page=10`)
                .then(response => response.json())
                .then(({ items, total_pages }) => {
                    setSearchedAddress(address)
                    setPriceData(items);
                    setTotalPages(total_pages);
                    setLoading(false);
                })
                .catch(error => {
                    console.error('Error fetching price data by address:', error);
                    setLoading(false);
                });
        }
    }, [address, page]);  // Include address in the dependencies


    const handleOpenDetails = (data) => {
        setSelectedData(data);
    };

    const handleCloseDetails = () => {
        setSelectedData(null);
    };

    const handleChangePage = (event, value) => {
        setPage(value);
    };

    const getChipColor = (value) => value === searchedAddress ? 'info' : 'default';

    if (loading) return <CircularProgress />;

    return (
        <Grid container spacing={2} sx={{ padding: 2 }}>
            <Typography variant="h4" gutterBottom width={"100%"}>
                NFT Address Analytics
            </Typography>
            {priceData.map((data, index) => (
                <Grid item xs={12} md={6} key={index} onClick={() => handleOpenDetails(data)}>
                    <Card raised sx={{ minHeight: 200, cursor: 'pointer' }}>
                        <CardContent>
                            <Grid container spacing={2} alignItems="center">
                                <Grid item xs={12}>
                                    <Chip label={data.transaction_hash} component={Link} to={`/transactions/${data.transaction_hash}`} clickable color={getChipColor(data.transaction_hash)} variant="outlined" />
                                </Grid>
                                {Object.entries(data).map(([key, value]) => (
                                    <Grid item xs={6} key={key}>
                                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{key.replace(/_/g, ' ')}:</Typography>
                                        <Chip label={value || "Unknown"} color={getChipColor(value)} variant="outlined" />
                                    </Grid>
                                ))}
                            </Grid>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
            <Grid item xs={12}>
                <Pagination count={totalPages} page={page} onChange={handleChangePage} color="primary"
                            sx={{ display: 'flex', justifyContent: 'center', padding: 2 }}/>
            </Grid>
            {selectedData && (
                <Dialog open={Boolean(selectedData)} onClose={handleCloseDetails} fullWidth maxWidth="md">
                    <DialogTitle>NFT Price Details</DialogTitle>
                    <DialogContent dividers>
                        <Grid container spacing={2} alignItems="center">
                            {Object.entries(selectedData).map(([key, value]) => (
                                <Grid item xs={6} key={key}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{key.replace(/_/g, ' ')}:</Typography>
                                    <Chip label={value || "Unknown"} color={getChipColor(value)} variant="outlined" />
                                </Grid>
                            ))}
                        </Grid>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseDetails} color="primary" autoFocus>Close</Button>
                    </DialogActions>
                </Dialog>
            )}
        </Grid>
    );
}

export default AddressAnalytics;
