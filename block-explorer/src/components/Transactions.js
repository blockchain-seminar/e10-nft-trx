import React, {useState, useEffect} from 'react';
import {Link as RouterLink} from 'react-router-dom';
import {
    Card,
    CardContent,
    Typography,
    Link,
    Stack,
    Pagination,
    useTheme,
    Grid,
    Paper,
    Chip,
    Divider
} from '@mui/material';

function Transactions() {
    const [transactions, setTransactions] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const theme = useTheme();

    const fetchTransactions = (page) => {
        fetch(`http://127.0.0.1:5000/transactions/latest?page=${page}&per_page=10`)
            .then(response => response.json())
            .then(({ items, total_pages }) => {
                setTransactions(items);
                setTotalPages(total_pages);
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
        <div style={{margin: theme.spacing(3)}}>
            <Typography variant="h4" gutterBottom>
                Latest Transactions
            </Typography>
            <Grid container spacing={2}>
                {transactions.map((tx, index) => (
                    <Grid item xs={12} md={6} key={tx.transaction_hash}>
                        <Card raised sx={{backgroundColor: theme.palette.background.paper}}>
                            <CardContent>
                                <Grid container spacing={2} alignItems="center">
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Transaction:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Chip label={tx.transaction_hash} component={RouterLink}
                                              to={`/transactions/${tx.transaction_hash}`} clickable variant="outlined"
                                              color="primary"/>
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>
                                            Block Number:
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Chip label={tx.block_number} variant={"outlined"} />
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                    ))}
            </Grid>
            <Grid sx={{display: 'flex', justifyContent: 'center', padding: 2, marginTop: 2}}>
                <Pagination count={totalPages} page={page} onChange={handleChangePage} color="primary"/>
            </Grid>
        </div>
);
}

export default Transactions;
