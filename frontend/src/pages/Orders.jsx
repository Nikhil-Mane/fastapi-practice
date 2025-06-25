import { useEffect, useState } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Snackbar from '@mui/material/Snackbar';
import Chip from '@mui/material/Chip';

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      setMessage('');
      const token = localStorage.getItem('token');
      if (!token) {
        setMessage('Please login to view your orders.');
        setSnackbarOpen(true);
        setLoading(false);
        return;
      }
      try {
        const res = await fetch('http://localhost:8000/orders/my', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setOrders(data);
        } else {
          setMessage('Failed to load orders.');
          setSnackbarOpen(true);
        }
      } catch {
        setMessage('Network error');
        setSnackbarOpen(true);
      }
      setLoading(false);
    };
    fetchOrders();
  }, []);

  const statusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'processed': return 'success';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <div>
      <Typography variant="h4" sx={{ mb: 3 }}>Your Orders</Typography>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={message}
      />
      {loading ? <Typography>Loading...</Typography> : (
        orders.length === 0 ? <Typography>No orders found.</Typography> : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Order ID</TableCell>
                  <TableCell>Product ID</TableCell>
                  <TableCell>Quantity</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created At</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.map(order => (
                  <TableRow key={order.id}>
                    <TableCell>{order.id}</TableCell>
                    <TableCell>{order.product_id}</TableCell>
                    <TableCell>{order.quantity}</TableCell>
                    <TableCell>
                      <Chip label={order.status} color={statusColor(order.status)} size="small" />
                    </TableCell>
                    <TableCell>{order.created_at}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )
      )}
    </div>
  );
}

export default Orders; 