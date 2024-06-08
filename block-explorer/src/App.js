import React, {useState} from 'react';
import {
    CssBaseline,
    Container,
    AppBar,
    Toolbar,
    Typography,
    Link,
    ThemeProvider,
    createTheme,
    InputBase, Button
} from '@mui/material';
import {BrowserRouter as Router, Routes, Route, NavLink} from 'react-router-dom';

import Transactions from './components/Transactions';
import Blocks from './components/Blocks';
import Marketplaces from './components/Marketplaces';
import ABIs from './components/ABIs';
import TransactionDetail from './components/TransactionDetail';
import BlockDetail from "./components/BlockDetail";
import V_NFT_PriceData from "./components/V_NFT_PriceData";
import DataProcessingForm from "./components/DataProcessingForm";
import AddressAnalytics from "./components/AddressAnalytics";
import SearchResults from "./components/SearchResults";

// Create a theme instance.
const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#bb86fc',
        },
        secondary: {
            main: '#03dac6',
        },
        background: {
            default: '#121212',
            paper: '#1e1e1e',
        },
        text: {
            primary: '#ffffff',
            secondary: '#e0e0e0',
        },
    },
    typography: {
        fontFamily: 'Roboto, sans-serif',
        h6: {
            fontWeight: 500,
        },
    },
});

function App() {
    const [searchTerm, setSearchTerm] = useState('');


    return (
        <ThemeProvider theme={darkTheme}>
            <Router>
                <CssBaseline />
                <AppBar position="static">
                    <Toolbar>
                        <Typography variant="h6" color="inherit" noWrap>
                            NFT TRX Explorer
                        </Typography>
                        {['/Price_Data', '/Transactions', '/Blocks', '/Marketplaces', '/ABIs', '/Update_DB'].map((path, index) => (
                            <Link
                                key={index}
                                component={NavLink}
                                to={path.toLowerCase()}
                                color="inherit"
                                style={{ marginLeft: 20 }}
                                sx={{
                                    textDecoration: 'none',
                                    '&.active': {
                                        color: darkTheme.palette.secondary.main,
                                        textDecoration: 'underline'
                                    }
                                }}
                            >
                                {path.substr(1).replace(/_/g, ' ')}
                            </Link>
                        ))}
                        <InputBase
                            placeholder="Search…"
                            inputProps={{ 'aria-label': 'search' }}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{ marginLeft: 20, flex: 1 }}
                        />
                        <Link component={NavLink} to={`/search_results/${searchTerm}`} sx={{textDecoration: 'none'}}>Search</Link>
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
                        <Route path="/update_db" element={<DataProcessingForm />} />
                        <Route path="/address_analytics/:address" element={<AddressAnalytics />} />
                        <Route path="/search_results/:query" element={<SearchResults />} />
                    </Routes>
                </Container>
            </Router>
        </ThemeProvider>
    );
}

export default App;
