import React, { useEffect, useState } from 'react';
import {Link as RouterLink, useParams} from 'react-router-dom';
import {
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Chip,
    Stack,
    Divider,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    useTheme,
    Grid
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
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={4}>
                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>Block Number:</Typography>
                        </Grid>
                        <Grid item xs={8}>
                            <Chip label={transaction?.block_number} variant={"outlined"} />
                        </Grid>
                        <Grid item xs={4}>
                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>Chain ID:</Typography>
                        </Grid>
                        <Grid item xs={8}>
                            {transaction?.chain_id}
                        </Grid>

                        <Divider sx={{my: 1, width: '100%'}}/>

                        <Grid item xs={4}>
                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>From:</Typography>
                        </Grid>
                        <Grid item xs={8}>
                            <Chip label={transaction?.from_address} variant="outlined" color="warning" />
                        </Grid>
                        <Grid item xs={4}>
                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>To:</Typography>
                        </Grid>
                        <Grid item xs={8}>
                            <Chip label={transaction?.to_address} variant="outlined" color="info" />
                        </Grid>

                        <Divider sx={{my: 1, width: '100%'}}/>

                        <Grid item xs={4}>
                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>Gas:</Typography>
                        </Grid>
                        <Grid item xs={8}>
                            {transaction?.gas}
                        </Grid>

                        <Grid item xs={4}>
                            <Typography variant="body1" sx={{fontWeight: 'bold'}}>Gas Price:</Typography>
                        </Grid>
                        <Grid item xs={8}>
                            {transaction?.gas_price}
                        </Grid>

                        <Divider sx={{my: 1, width: '100%'}}/>

                        <Grid item xs={12}>
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
                                                        <span style={{lineBreak: "anywhere"}}>{value}</span>
                                                    </Typography>
                                                );
                                            }
                                            return null;
                                        })}
                                    </Stack>
                                </AccordionDetails>
                            </Accordion>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Box>
    );
}

export default TransactionDetail;
