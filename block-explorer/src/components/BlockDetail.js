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
    DialogActions
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
                                <Typography variant="h6" gutterBottom>
                                    Transaction Hash: <Chip label={transaction.transaction_hash} variant="outlined" color="primary" />
                                </Typography>
                                <Typography variant="body2">
                                    From: <Chip label={transaction.from_address} color="secondary" />
                                </Typography>
                                <Typography variant="body2">
                                    To: <Chip label={transaction.to_address} color="secondary" />
                                </Typography>
                                <Typography variant="body2">
                                    Value: {transaction.value} ETH
                                </Typography>
                                <Typography variant="body2">
                                    Gas Used: {transaction.gas}
                                </Typography>
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
