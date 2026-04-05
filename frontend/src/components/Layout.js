import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '@mui/material/styles';
import {
  AppBar, Box, Drawer, IconButton, List, ListItem, ListItemButton,
  ListItemIcon, ListItemText, Toolbar, Typography, Avatar, Menu,
  MenuItem, Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Alert, InputAdornment, Divider
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard as DashboardIcon, Science as ScienceIcon,
  Psychology as PsychologyIcon, Assessment as AssessmentIcon,
  Description as DescriptionIcon, AccountCircle, Logout,
  Edit as EditIcon, Visibility, VisibilityOff
} from '@mui/icons-material';
import { removeToken } from '../utils/auth';
import { authAPI } from '../services/api';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Compounds', icon: <ScienceIcon />, path: '/compounds' },
  { text: 'Predictions', icon: <PsychologyIcon />, path: '/predictions' },
  { text: 'Experiments', icon: <AssessmentIcon />, path: '/experiments' },
  { text: 'Reports', icon: <DescriptionIcon />, path: '/reports' },
];

export default function Layout({ children }) {
  const theme = useTheme();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [user, setUser] = useState(null);

  // Profile Settings State
  const [profileOpen, setProfileOpen] = useState(false);
  const [isEditingMode, setIsEditingMode] = useState(false);

  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editPassword, setEditPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [profileError, setProfileError] = useState('');
  const [profileSuccess, setProfileSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    authAPI.getMe()
      .then(response => {
        setUser(response.data);
        setEditName(response.data.full_name || '');
        setEditEmail(response.data.email || '');
      })
      .catch(err => console.error("Could not fetch user info", err));
  }, []);

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);
  const handleMenuClick = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);

  const handleLogout = () => {
    removeToken();
    navigate('/login');
  };

  const openProfileSettings = () => {
    handleMenuClose();
    setProfileError('');
    setProfileSuccess('');
    setEditPassword('');
    setIsEditingMode(false);
    setProfileOpen(true);
  };

  const validateProfile = () => {
    const nameRegex = /^[a-zA-Z\s]{2,50}$/;
    if (!nameRegex.test(editName.trim())) {
      setProfileError('Full name must be 2-50 characters and contain only letters.');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(editEmail)) {
      setProfileError('Please enter a valid email address.');
      return false;
    }

    if (editPassword) {
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      if (!passwordRegex.test(editPassword)) {
        setProfileError('Password must be 8+ chars with 1 uppercase, 1 lowercase, 1 number, and 1 symbol.');
        return false;
      }
    }
    return true;
  };

  const handleSaveProfile = async () => {
    setProfileError('');
    setProfileSuccess('');
    if (!validateProfile()) return;

    setSaving(true);
    try {
      const updateData = {
        full_name: editName.trim(),
        email: editEmail.toLowerCase(),
      };
      if (editPassword) updateData.password = editPassword;

      const response = await authAPI.updateMe(updateData);
      setUser(response.data);
      setProfileSuccess('Profile updated successfully!');
      setEditPassword('');

      setTimeout(() => {
        setIsEditingMode(false);
        setProfileSuccess('');
      }, 1500);

    } catch (err) {
      setProfileError('Failed to update profile. ' + (err.response?.data?.detail || ''));
    } finally {
      setSaving(false);
    }
  };

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold', color: theme.palette.primary.main }}>
          Drugovery
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 1, px: 2 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                setMobileOpen(false);
              }}
              sx={{
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: theme.palette.primary.main + '15',
                  borderLeft: `4px solid ${theme.palette.primary.main}`,
                }
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? theme.palette.primary.main : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} sx={{ fontWeight: location.pathname === item.path ? '600' : '500' }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ width: { sm: `calc(100% - ${drawerWidth}px)` }, ml: { sm: `${drawerWidth}px` } }}>
        <Toolbar>
          <IconButton color="inherit" aria-label="open drawer" edge="start" onClick={handleDrawerToggle} sx={{ mr: 2, display: { sm: 'none' } }}>
            <MenuIcon />
          </IconButton>

          <Box sx={{ flexGrow: 1 }} />

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>

            <Typography variant="body2" sx={{ display: { xs: 'none', md: 'block' }, fontWeight: 600 }}>
              {user?.full_name || 'Loading...'}
            </Typography>

            <IconButton onClick={handleMenuClick} size="small" sx={{ p: 0 }}>
              <Avatar sx={{ width: 40, height: 40, bgcolor: theme.palette.primary.main, color: '#fff', fontWeight: 'bold' }}>
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : <AccountCircle />}
              </Avatar>
            </IconButton>
          </Box>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            PaperProps={{
              elevation: 0,
              sx: {
                overflow: 'visible',
                filter: 'drop-shadow(0px 4px 10px rgba(0,0,0,0.1))',
                mt: 1.5,
                borderRadius: 2,
                border: '1px solid #f1f5f9'
              },
            }}
          >
            <MenuItem onClick={openProfileSettings}>
              <ListItemIcon><AccountCircle fontSize="small" /></ListItemIcon>
              My Profile
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
              <ListItemIcon><Logout fontSize="small" color="error" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
        <Drawer variant="temporary" open={mobileOpen} onClose={handleDrawerToggle} ModalProps={{ keepMounted: true }} sx={{ display: { xs: 'block', sm: 'none' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth } }}>
          {drawer}
        </Drawer>
        <Drawer variant="permanent" sx={{ display: { xs: 'none', sm: 'block' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, borderRight: 'none', boxShadow: '1px 0 10px rgba(0,0,0,0.03)' } }} open>
          {drawer}
        </Drawer>
      </Box>

      <Box component="main" sx={{ flexGrow: 1, p: 4, width: { sm: `calc(100% - ${drawerWidth}px)` } }}>
        <Toolbar />
        {children}
      </Box>

      {/* DYNAMIC PROFILE DIALOG */}
      <Dialog open={profileOpen} onClose={() => setProfileOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 'bold' }}>
          {isEditingMode ? 'Edit Profile' : 'My Profile'}
        </DialogTitle>
        <Divider />
        <DialogContent>
          {!isEditingMode ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Avatar sx={{ width: 90, height: 90, margin: '0 auto', mb: 2, bgcolor: theme.palette.primary.main, color: '#fff', fontSize: '2.5rem', fontWeight: 'bold' }}>
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : '?'}
              </Avatar>
              <Typography variant="h5" gutterBottom fontWeight="bold">
                {user?.full_name}
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                {user?.email}
              </Typography>
              <Button
                startIcon={<EditIcon />}
                variant="outlined"
                sx={{ mt: 4, borderRadius: 2 }}
                onClick={() => setIsEditingMode(true)}
              >
                Edit Details
              </Button>
            </Box>
          ) : (
            <Box sx={{ mt: 1 }}>
              {profileError && <Alert severity="error" sx={{ mb: 2 }}>{profileError}</Alert>}
              {profileSuccess && <Alert severity="success" sx={{ mb: 2 }}>{profileSuccess}</Alert>}

              <TextField margin="normal" required fullWidth label="Full Name" value={editName} onChange={(e) => setEditName(e.target.value)} />
              <TextField margin="normal" required fullWidth label="Email Address" type="email" value={editEmail} onChange={(e) => setEditEmail(e.target.value)} />
              <TextField
                margin="normal"
                fullWidth
                label="New Password (leave blank to keep current)"
                type={showPassword ? 'text' : 'password'}
                value={editPassword}
                onChange={(e) => setEditPassword(e.target.value)}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          )}
        </DialogContent>
        {isEditingMode && (
          <DialogActions sx={{ p: 3, pt: 0 }}>
            <Button onClick={() => setIsEditingMode(false)} color="inherit">Cancel</Button>
            <Button onClick={handleSaveProfile} variant="contained" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogActions>
        )}
      </Dialog>
    </Box>
  );
}