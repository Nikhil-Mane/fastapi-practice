import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { Link as RouterLink } from 'react-router-dom';
import Link from '@mui/material/Link';

function Navbar({ isAuthenticated, isAdmin, onLogout }) {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          <Link component={RouterLink} to="/" color="inherit" underline="none">
            E-Commerce
          </Link>
          <Link component={RouterLink} to="/products" color="inherit" underline="none" sx={{ ml: 2 }}>
            Products
          </Link>
          <Link component={RouterLink} to="/cart" color="inherit" underline="none" sx={{ ml: 2 }}>
            Cart
          </Link>
          {isAuthenticated && (
            <Link component={RouterLink} to="/orders" color="inherit" underline="none" sx={{ ml: 2 }}>
              Orders
            </Link>
          )}
          {isAdmin && (
            <Link component={RouterLink} to="/admin" color="inherit" underline="none" sx={{ ml: 2 }}>
              Admin
            </Link>
          )}
        </Typography>
        {isAuthenticated ? (
          <Button color="inherit" onClick={onLogout}>Logout</Button>
        ) : (
          <>
            <Button color="inherit" component={RouterLink} to="/login">Login</Button>
            <Button color="inherit" component={RouterLink} to="/register">Register</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}

export default Navbar; 