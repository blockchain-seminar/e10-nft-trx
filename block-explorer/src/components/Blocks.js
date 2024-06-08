import React, { useState, useEffect } from 'react';
import {
    Typography, Card, CardContent, Chip, Pagination, Grid, useTheme,
    Link as MuiLink
} from '@mui/material';
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
                setTotalPages(3); // Adjust based on your actual data
            })
            .catch(error => console.error('Error fetching blocks:', error));
    };

    const handleChangePage = (event, value) => {
        setPage(value);
        fetchBlocks(value);
    };
    useEffect(() => {
        fetchBlocks(page);
    }, [page]);

    return (
        <div style={{ margin: theme.spacing(3) }}>
            <Typography variant="h4" gutterBottom>
                Fetched Blocks
            </Typography>
            <Grid container spacing={2}>
                {blocks.map((block, index) => (
                    <Grid item xs={12} md={6} key={index}>
                        <RouterLink to={`/blocks/${block.block_number}`} style={{ textDecoration: 'none' }}>
                            <Card raised sx={{
                                backgroundColor: theme.palette.background.paper,
                                transition: "0.3s",
                                '&:hover': {
                                    boxShadow: theme.shadows[10]
                                },
                                cursor: 'pointer'
                            }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Block Number: {block.block_number}
                                    </Typography>
                                    <Chip label={`Fetched Date: ${block.fetched_dt}`} variant="outlined" color="secondary" />
                                </CardContent>
                            </Card>
                        </RouterLink>
                    </Grid>
                ))}
            </Grid>
            <Pagination
                count={totalPages}
                page={page}
                onChange={handleChangePage}
                color="primary"
                sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}
            />
        </div>
    );
}

export default Blocks;
