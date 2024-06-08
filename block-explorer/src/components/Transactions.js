import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Card, CardContent, Typography, Link, Stack, Pagination, useTheme, Grid, Paper, Chip } from '@mui/material';

function Transactions() {
    const [transactions, setTransactions] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const theme = useTheme();

    const fetchTransactions = (page) => {
        fetch(`http://127.0.0.1:5000/transactions/latest?page=${page}&per_page=10`)
            .then(response => response.json())
            .then(data => {
                setTransactions(data);
                setTotalPages(5); // Assuming 50 transactions total, adjust based on your actual data
            })
            .catch(error => console.error('Error fetching transactions:', error));
    };

    useEffect(() => {
        fetchTransactions(page);
    }, [page]);

    const handleChangePage = (event, value) => {
        setPage(value);
        fetchTransactions(value);
    };

    return (
        <div style={{ margin: theme.spacing(3) }}>
            <Typography variant="h4" gutterBottom>
                Latest Transactions
            </Typography>
            <Grid container spacing={2}>
                {transactions.map((tx, index) => (
                    <Grid item xs={12} md={6} key={tx.transaction_hash}>
                        <Card raised sx={{ backgroundColor: theme.palette.background.paper }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Transaction: <Chip label={tx.transaction_hash} component={RouterLink} to={`/transactions/${tx.transaction_hash}`} clickable variant="outlined" color="primary"/>
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Block Number: <Chip label={tx.block_number} size="small" />
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            <Paper sx={{ display: 'flex', justifyContent: 'center', padding: 2, marginTop: 2 }}>
                <Pagination count={totalPages} page={page} onChange={handleChangePage} color="primary" />
            </Paper>
        </div>
    );
}

export default Transactions;
