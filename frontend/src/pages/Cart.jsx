import { useEffect, useState } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Snackbar from '@mui/material/Snackbar';

function Cart() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const fetchCart = async () => {
    setLoading(true);
    setMessage('');
    const token = localStorage.getItem('token');
    if (!token) {
      setMessage('Please login to view your cart.');
      setLoading(false);
      setSnackbarOpen(true);
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/cart/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setItems(data);
      } else {
        setMessage('Failed to load cart.');
        setSnackbarOpen(true);
      }
    } catch {
      setMessage('Network error');
      setSnackbarOpen(true);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCart();
    // eslint-disable-next-line
  }, []);

  const handleRemove = async (productId) => {
    setMessage('');
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:8000/cart/remove', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
      });
      if (res.ok) {
        setMessage('Item removed.');
        setSnackbarOpen(true);
        fetchCart();
      } else {
        setMessage('Failed to remove item.');
        setSnackbarOpen(true);
      }
    } catch {
      setMessage('Network error');
      setSnackbarOpen(true);
    }
  };

  const handlePlaceOrder = async () => {
    setMessage('');
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:8000/orders/from_cart', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setMessage('Order placed!');
        setSnackbarOpen(true);
        fetchCart();
      } else {
        setMessage('Failed to place order.');
        setSnackbarOpen(true);
      }
    } catch {
      setMessage('Network error');
      setSnackbarOpen(true);
    }
  };

  return (
    <div>
      <Typography variant="h4" sx={{ mb: 3 }}>Your Shopping Cart</Typography>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={message}
      />
      {loading ? <Typography>Loading...</Typography> : (
        items.length === 0 ? <Typography>Your cart is empty.</Typography> : (
          <>
            <TableContainer component={Paper} sx={{ mb: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Product ID</TableCell>
                    <TableCell>Quantity</TableCell>
                    <TableCell>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items.map(item => (
                    <TableRow key={item.id}>
                      <TableCell>{item.product_id}</TableCell>
                      <TableCell>{item.quantity}</TableCell>
                      <TableCell>
                        <Button color="error" variant="outlined" onClick={() => handleRemove(item.product_id)}>
                          Remove
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Button variant="contained" color="primary" onClick={handlePlaceOrder}>Place Order</Button>
          </>
        )
      )}
    </div>
  );
}

export default Cart; 