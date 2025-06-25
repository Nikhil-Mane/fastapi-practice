import { useEffect, useState } from 'react';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

function ProductCard({ product, onAddToCart }) {
  return (
    <Card sx={{ minWidth: 250, maxWidth: 300, m: 1 }}>
      <CardContent>
        <Typography variant="h6">{product.name}</Typography>
        <Typography variant="body2" color="text.secondary">{product.description}</Typography>
        <Typography sx={{ mt: 1 }}><b>Price:</b> ${product.price}</Typography>
        <Typography><b>Stock:</b> {product.stock}</Typography>
      </CardContent>
      <CardActions>
        <Button size="small" variant="contained" onClick={() => onAddToCart(product.id)} disabled={product.stock < 1}>
          Add to Cart
        </Button>
      </CardActions>
    </Card>
  );
}

function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/products/?limit=20')
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      });
  }, []);

  const handleAddToCart = async (productId) => {
    setMessage('');
    const token = localStorage.getItem('token');
    if (!token) {
      setMessage('Please login to add to cart.');
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/cart/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
      });
      if (res.ok) {
        setMessage('Added to cart!');
      } else {
        const data = await res.json();
        setMessage(data.detail || 'Failed to add to cart');
      }
    } catch (err) {
      setMessage('Network error');
    }
  };

  return (
    <div>
      <Typography variant="h4" sx={{ mb: 3 }}>Product Catalog</Typography>
      {message && <Typography color={message === 'Added to cart!' ? 'success.main' : 'error.main'}>{message}</Typography>}
      {loading ? <Typography>Loading...</Typography> : (
        <Grid container spacing={2}>
          {products.map(product => (
            <Grid item key={product.id} xs={12} sm={6} md={4} lg={3}>
              <ProductCard product={product} onAddToCart={handleAddToCart} />
            </Grid>
          ))}
        </Grid>
      )}
    </div>
  );
}

export default Home; 