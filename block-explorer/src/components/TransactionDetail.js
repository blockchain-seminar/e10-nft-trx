import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
    Card, CardContent, Typography, CircularProgress, Chip, Stack, Divider, Accordion, AccordionSummary, AccordionDetails, useTheme
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Box } from '@mui/system';

function TransactionDetail({selectedTransaction}) {
    const { transactionHash } = useParams();
    const [transaction, setTransaction] = useState(null);
    const [loading, setLoading] = useState(true);
    const theme = useTheme();


    useEffect(() => {
        if (selectedTransaction === undefined){
            fetch(`http://127.0.0.1:5000/transactions/${transactionHash}`)
                .then(response => response.json())
                .then(data => {
                    setTransaction(data);
                    setLoading(false);
                })
                .catch(error => {
                    console.error('Error fetching transaction details:', error);
                    setLoading(false);
                });
        } else {
            setTransaction(selectedTransaction);
            setLoading(false);
        }
    }, [transactionHash, selectedTransaction]);

    if (loading) return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <CircularProgress />
        </Box>
    );

    return (
        <Box sx={{ maxWidth: 800, mx: 'auto', my: 4 }}>
            <Card raised sx={{ backgroundColor: theme.palette.background.paper, boxShadow: theme.shadows[4] }}>
                <CardContent>
                    {!selectedTransaction && <>
                        <Typography variant="h5" gutterBottom color="primary" sx={{ fontWeight: 'bold' }}>
                            Transaction Details
                        </Typography>
                        <Divider sx={{ my: 2 }} />
                    </> }
                    <Stack spacing={2} divider={<Divider flexItem />}>
                        {/* Essential Information */}
                        <Typography variant="subtitle1">
                            <strong>Block Number:</strong> {transaction?.block_number}
                        </Typography>
                        <Typography variant="subtitle1">
                            <strong>Chain ID:</strong> {transaction?.chain_id}
                        </Typography>
                        <Typography variant="subtitle1">
                            <strong>From:</strong> <Chip label={transaction?.from_address} variant="outlined" color="primary" />
                        </Typography>
                        <Typography variant="subtitle1">
                            <strong>To:</strong> <Chip label={transaction?.to_address} variant="outlined" color="secondary" />
                        </Typography>
                        <Typography variant="subtitle1">
                            <strong>Gas:</strong> {transaction?.gas}
                        </Typography>
                        <Typography variant="subtitle1">
                            <strong>Gas Price:</strong> {transaction?.gas_price}
                        </Typography>

                        {/* Accordion for Additional Details */}
                        <Accordion>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography>More Information</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Stack spacing={1}>
                                    {Object.entries(transaction || {}).map(([key, value]) => {
                                        if (!['block_number', 'chain_id', 'from_address', 'to_address', 'gas', 'gas_price'].includes(key)) {
                                            return (
                                                <Typography key={key} variant="body2">
                                                    <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong>
                                                    {value}
                                                </Typography>
                                            );
                                        }
                                        return null;
                                    })}
                                </Stack>
                            </AccordionDetails>
                        </Accordion>
                    </Stack>
                </CardContent>
            </Card>
        </Box>
    );
}

export default TransactionDetail;
