import React from 'react';
import { CssBaseline, Container, AppBar, Toolbar, Typography, Link } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';

import Transactions from './components/Transactions';
import Blocks from './components/Blocks';
import Marketplaces from './components/Marketplaces';
import ABIs from './components/ABIs';
import TransactionDetail from './components/TransactionDetail';
import BlockDetail from "./components/BlockDetail";
import V_NFT_PriceData from "./components/V_NFT_PriceData";

function App() {
    return (
        <Router>
            <CssBaseline />
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" color="inherit" noWrap>
                        NFT TRX Explorer
                    </Typography>
                    <Link component={NavLink} to="/price_data" color="inherit" style={{ marginLeft: 20 }}>
                        NFT Price Data
                    </Link>
                    <Link component={NavLink} to="/transactions" color="inherit" style={{ marginLeft: 20 }}>
                        Transactions
                    </Link>
                    <Link component={NavLink} to="/blocks" color="inherit" style={{ marginLeft: 20 }}>
                        Blocks
                    </Link>
                    <Link component={NavLink} to="/marketplaces" color="inherit" style={{ marginLeft: 20 }}>
                        Marketplaces
                    </Link>
                    <Link component={NavLink} to="/abis" color="inherit" style={{ marginLeft: 20 }}>
                        ABIs
                    </Link>
                </Toolbar>
            </AppBar>
            <Container>
                <Routes>
                    <Route path="/price_data" element={<V_NFT_PriceData />} />
                    <Route path="/blocks/:blockNumber" element={<BlockDetail />} />
                    <Route path="/transactions" element={<Transactions />} />
                    <Route path="/transactions/:transactionHash" element={<TransactionDetail />} />
                    <Route path="/blocks" element={<Blocks />} />
                    <Route path="/marketplaces" element={<Marketplaces />} />
                    <Route path="/abis" element={<ABIs />} />
                </Routes>
            </Container>
        </Router>
    );
}

export default App;
