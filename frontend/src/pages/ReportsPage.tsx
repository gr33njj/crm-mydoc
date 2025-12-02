import { useState } from 'react';
import { Typography, TextField, Button, Paper, Box } from '@mui/material';
import api from '../api/axios';

export const ReportsPage = () => {
  const [report, setReport] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');

  const generateReport = async () => {
    try {
      const res = await api.get('/reports', { params: { start, end } });
      setReport(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>Генерация отчетов</Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField type="date" label="Начало периода" InputLabelProps={{ shrink: true }} value={start} onChange={(e) => setStart(e.target.value)} />
        <TextField type="date" label="Конец периода" InputLabelProps={{ shrink: true }} value={end} onChange={(e) => setEnd(e.target.value)} />
        <Button variant="contained" onClick={generateReport}>Сформировать</Button>
      </Box>
      {report && (
        <Paper sx={{ p: 3, whiteSpace: 'pre-wrap' }}>
          <Typography>{report}</Typography>
        </Paper>
      )}
    </div>
  );
};
