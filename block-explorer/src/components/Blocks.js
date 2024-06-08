import React, { useState, useEffect } from 'react';
import {
    Typography, Card, CardContent, Chip, Pagination, Grid, useTheme,
    Link as MuiLink, Divider
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
            .then(({ items, total_pages }) => {
                setBlocks(items);
                setTotalPages(total_pages);
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
                                    <Grid container spacing={2} alignItems="center">
                                        <Grid item xs={4}>
                                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>Block Number:</Typography>
                                        </Grid>
                                        <Grid item xs={8}>
                                            <Chip label={block.block_number} variant={"outlined"} />
                                        </Grid>
                                        <Divider sx={{my: 1, width: '100%'}}/>
                                        <Grid item xs={4}>
                                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>Fetched Date:</Typography>
                                        </Grid>
                                        <Grid item xs={8}>
                                            <Chip label={`${block.fetched_dt}`} variant="outlined" color="secondary" />
                                        </Grid>
                                        <Divider sx={{my: 1, width: '100%'}}/>
                                    </Grid>
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
