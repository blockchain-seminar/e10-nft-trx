import React, { useState, useEffect } from 'react';
import {
    Typography, Card, CardContent, Chip, Grid, CircularProgress, Pagination,
    Dialog, DialogTitle, DialogContent, Button, Divider, DialogActions
} from '@mui/material';
import { useParams } from 'react-router-dom';
import { Link } from 'react-router-dom';

function SearchResults() {
    const { query } = useParams();
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedData, setSelectedData] = useState(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/search_price_data?query=${query}&page=${page}&per_page=10`)
            .then(response => response.json())
            .then(({ items, total_pages }) => {
                setData(items);
                setTotalPages(total_pages);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                setLoading(false);
            });
    }, [query, page]);

    const handleOpenDetails = (item) => {
        setSelectedData(item);
    };

    const handleCloseDetails = () => {
        setSelectedData(null);
    };

    const handleChangePage = (event, value) => {
        setPage(value);
    };

    const getChipColor = (key, value) => {

        if (typeof value === 'string' && value.includes(query)) {
            return 'info';
        }
        return 'default';
    };

    if (loading) return <CircularProgress />;

    return (
        <Grid container spacing={2} sx={{ padding: 2 }}>
            <Typography variant="h4" gutterBottom>
                Search Results for "{query}"
            </Typography>
            {data.map((item, index) => (
                <Grid item xs={12} md={6} key={index} onClick={() => handleOpenDetails(item)}>
                    <Card raised sx={{ minHeight: 200, cursor: 'pointer' }}>
                        <CardContent>
                            <Grid container spacing={2} alignItems="center">
                                {Object.entries(item).map(([key, value]) => (
                                    <Grid item xs={12} key={key}>
                                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                                            {key.replace(/_/g, ' ')}:
                                        </Typography>
                                        <Chip label={value || "Unknown"} color={getChipColor(key, value)} variant="outlined" />
                                    </Grid>
                                ))}
                            </Grid>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
            <Pagination count={totalPages} page={page} onChange={handleChangePage} color="primary"
                        sx={{ display: 'flex', justifyContent: 'center', padding: 2 }}/>
            {selectedData && (
                <Dialog open={Boolean(selectedData)} onClose={handleCloseDetails} fullWidth maxWidth="md">
                    <DialogTitle>Detail View</DialogTitle>
                    <DialogContent dividers>
                        <Grid container spacing={2} alignItems="center">
                            {Object.entries(selectedData).map(([key, value]) => (
                                <Grid item xs={12} key={key}>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                                        {key.replace(/_/g, ' ')}:
                                    </Typography>
                                    <Chip label={value || "Unknown"} color={getChipColor(key, value)} variant="outlined" />
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

export default SearchResults;
