import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
    Grid,
    Card,
    CardContent,
    Typography,
    Chip,
    CircularProgress,
    Box,
    Dialog,
    DialogContent,
    DialogTitle,
    Button,
    DialogActions, Divider
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import TransactionDetail from "./TransactionDetail";

function BlockDetail() {
    const { blockNumber } = useParams();
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedTransaction, setSelectedTransaction] = useState(null);
    const theme = useTheme();

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/blocks/${blockNumber}/transactions`)
            .then(response => response.json())
            .then(data => {
                setTransactions(data);
                console.log(data)
                setLoading(false);
            })
            .catch(error => {
                console.error(`Error fetching transactions for block ${blockNumber}:`, error);
                setLoading(false);
            });
    }, [blockNumber]);

    const handleOpenTransaction = (transaction) => {
        setSelectedTransaction(transaction);
    };

    const handleClose = () => {
        setSelectedTransaction(null);
    };

    if (loading) return <CircularProgress />;

    return (
        <Box sx={{ padding: theme.spacing(3) }}>
            <Typography variant="h4" gutterBottom>
                Transactions in Block {blockNumber}
            </Typography>
            <Grid container spacing={2}>
                {transactions.length > 0 ? transactions.map((transaction, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                        <Card raised sx={{ backgroundColor: theme.palette.background.paper, cursor: 'pointer' }} onClick={() => handleOpenTransaction(transaction)}>
                            <CardContent>
                                <Grid container spacing={2} alignItems="center">
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Transaction Hash:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Chip label={transaction.transaction_hash} variant="outlined" color="primary" />
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>From:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Chip label={transaction.from_address} variant="outlined" color="warning" />
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>To:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        <Chip label={transaction.to_address} variant="outlined" color="info" />
                                    </Grid>
                                    <Divider sx={{my: 1, width: '100%'}}/>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Value in ETH:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {transaction.value}
                                    </Grid>
                                    <Grid item xs={4}>
                                        <Typography variant="body1" sx={{fontWeight: 'bold'}}>Gas Used:</Typography>
                                    </Grid>
                                    <Grid item xs={8}>
                                        {transaction.gas}
                                    </Grid>

                                    <Divider sx={{my: 1, width: '100%'}}/>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                )) : (
                    <Typography variant="subtitle1">No transactions found in this block.</Typography>
                )}
            </Grid>
            {selectedTransaction && (
                <Dialog open={Boolean(selectedTransaction)} onClose={handleClose} fullWidth maxWidth="md">
                    <DialogTitle>Transaction Details</DialogTitle>
                    <DialogContent>
                        <TransactionDetail selectedTransaction={selectedTransaction} />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose} color="primary">Close</Button>
                    </DialogActions>
                </Dialog>
            )}
        </Box>
    );
}

export default BlockDetail;
