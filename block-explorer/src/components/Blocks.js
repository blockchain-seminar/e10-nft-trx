import React, { useState, useEffect } from 'react';
import { Typography, Card, CardContent, Chip, Pagination, Stack, Grid, useTheme, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

function Blocks() {
    const [blocks, setBlocks] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const theme = useTheme();

    const fetchBlocks = (page) => {
        fetch(`http://127.0.0.1:5000/blocks/fetched?page=${page}&per_page=10`)
            .then(response => response.json())
            .then(data => {
                setBlocks(data);
                setTotalPages(3); // Assuming there are 3 pages total, adjust based on actual data
            })
            .catch(error => console.error('Error fetching blocks:', error));
    };

    useEffect(() => {
        fetchBlocks(page);
    }, [page]);

    const handleChangePage = (event, value) => {
        setPage(value);
        fetchBlocks(value);
    };

    return (
        <div style={{ margin: theme.spacing(3) }}>
            <Typography variant="h4" gutterBottom>
                Fetched Blocks
            </Typography>
            <Grid container spacing={2}>
                {blocks.map((block, index) => (
                    <Grid item xs={12} md={6} key={index}>
                        <Card raised sx={{ backgroundColor: theme.palette.background.paper, transition: "0.3s", '&:hover': { boxShadow: theme.shadows[10] }}}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Block Number: {block.block_number}
                                </Typography>
                                <Chip label={`Fetched Date: ${block.fetched_dt}`} color="secondary" />
                                <br />
                                <Button
                                    component={RouterLink}
                                    to={`/blocks/${block.block_number}`}
                                    variant="outlined"
                                    color="primary"
                                    sx={{ mt: 2 }}
                                >
                                    View Transactions
                                </Button>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            <Pagination count={totalPages} page={page} onChange={handleChangePage} color="primary" sx={{ display: 'flex', justifyContent: 'center', mt: 2 }} />
        </div>
    );
}

export default Blocks;
