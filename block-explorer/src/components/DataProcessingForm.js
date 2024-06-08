import React, { useState } from 'react';
import { Button, FormControl, InputLabel, Select, MenuItem, TextField, Box } from '@mui/material';

function DataProcessingForm() {
    const [mode, setMode] = useState(3);  // Default mode
    const [n, setN] = useState(10);  // Default number of items

    const handleSubmit = (event) => {
        event.preventDefault();
        const dataToSend = { mode, n };

        fetch('http://127.0.0.1:5000/process_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataToSend),
        })
            .then(response => response.json())
            .then(data => {
                alert('Process started: ' + JSON.stringify(data));
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to start the process.');
            });
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="mode-select-label">Mode</InputLabel>
                <Select
                    labelId="mode-select-label"
                    id="mode-select"
                    value={mode}
                    label="Mode"
                    onChange={e => setMode(e.target.value)}
                >
                    <MenuItem value={1}>Mode 1</MenuItem>
                    <MenuItem value={2}>Mode 2</MenuItem>
                    <MenuItem value={3}>Mode 3</MenuItem>
                </Select>
            </FormControl>
            <TextField
                fullWidth
                label="Number of Items (n)"
                type="number"
                value={n}
                onChange={e => setN(parseInt(e.target.value, 10))}
                sx={{ mb: 2 }}
            />
            <Button type="submit" fullWidth variant="contained" color="primary">
                Start Process
            </Button>
        </Box>
    );
}

export default DataProcessingForm;
