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
import { Link } from 'react-router-dom';

function V_NFT_PriceData() {
    const [priceData, setPriceData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedData, setSelectedData] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/price_data?page=${page}&per_page=10`)
            .then(response => response.json())
            .then(({ items, total_pages }) => {
                setPriceData(items);
                setTotalPages(total_pages);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching price data:', error);
                setLoading(false);
            });
    }, [page]);

    const handleOpenDetails = (data) => {
        setSelectedData(data);
    };

    const handleCloseDetails = () => {
        setSelectedData(null);
    };

    const handleChangePage = (event, value) => {
        setPage(value);
    };

    if (loading) return <CircularProgress />;

    return (
        <Grid container spacing={2} sx={{ padding: 2 }}>
            <Typography variant="h4" gutterBottom width={"100%"}>
                NFT Price Data
            </Typography>
            {priceData.map((data, index) => (
                <Grid item xs={12} md={6} key={index} onClick={() => handleOpenDetails(data)}>
                    <Card raised sx={{ minHeight: 200, cursor: 'pointer' }}>
                        <CardContent>
                            <Grid container spacing={2} alignItems="center">
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Transaction:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={data.transaction_hash} component={Link} to={`/transactions/${data.transaction_hash}`} clickable variant="outlined" color="primary"/>
                                </Grid>
                                <Divider sx={{ my: 1, width: '100%' }}/>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Contract Type:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={data.contract_type || "Unknown"} variant="outlined" color="default"/>
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Value:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={`${data.transaction_value}`} variant="outlined" color="default"/>
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>ETH:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={`${data.transaction_value_eth}`} variant="outlined" color="default"/>
                                </Grid>
                                <Divider sx={{ my: 1, width: '100%' }}/>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>From:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={data.nft_from_address || "Unknown"} variant="outlined" color="warning"/>
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>To:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={data.nft_to_address || "Unknown"} variant="outlined" color="info"/>
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Collection:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={data.nft_collection || "Unknown"} variant="outlined" color="success"/>
                                </Grid>
                                <Grid item xs={4}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Token ID:</Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Chip label={data.nft_token_id || "Unknown"} variant="outlined" color="default"/>
                                </Grid>
                                <Divider sx={{ my: 1, width: '100%' }}/>
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
                    <DialogTitle>Transaction Details</DialogTitle>
                    <DialogContent dividers>
                        <Grid container spacing={2} alignItems="center">
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Transaction:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={selectedData.transaction_hash} component={Link} to={`/transactions/${selectedData.transaction_hash}`} clickable variant="outlined" color="primary"/>
                            </Grid>
                            <Divider sx={{ my: 1, width: '100%' }}/>
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Contract Type:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={selectedData.contract_type || "Unknown"} variant="outlined" color="default"/>
                            </Grid>
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Value:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={`${selectedData.transaction_value}`} variant="outlined" color="default"/>
                            </Grid>
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>ETH:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={`${selectedData.transaction_value_eth}`} variant="outlined" color="default"/>
                            </Grid>
                            <Divider sx={{ my: 1, width: '100%' }}/>
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>From:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={selectedData.nft_from_address || "Unknown"} variant="outlined" color="warning"/>
                            </Grid>
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>To:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={selectedData.nft_to_address || "Unknown"} variant="outlined" color="info"/>
                            </Grid>
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Collection:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={selectedData.nft_collection || "Unknown"} variant="outlined" color="success"/>
                            </Grid>
                            <Grid item xs={4}>
                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>Token ID:</Typography>
                            </Grid>
                            <Grid item xs={8}>
                                <Chip label={selectedData.nft_token_id || "Unknown"} variant="outlined" color="default"/>
                            </Grid>
                            <Divider sx={{ my: 1, width: '100%' }}/>
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

export default V_NFT_PriceData;
