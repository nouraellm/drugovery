import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
    Container, Paper, TextField, Button, Typography, Box,
    Alert, Link, InputAdornment, IconButton, Avatar
} from '@mui/material';
import { Visibility, VisibilityOff, Science as ScienceIcon } from '@mui/icons-material';
import { authAPI } from '../services/api';

export default function Signup() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const validateForm = () => {
        const nameRegex = /^[a-zA-Z\s]{2,50}$/;
        if (!nameRegex.test(fullName.trim())) {
            setError('Full name must be 2-50 characters and contain only letters.');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setError('Please enter a valid email address.');
            return false;
        }

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        if (!passwordRegex.test(password)) {
            setError('Password must be 8+ chars with 1 uppercase, 1 lowercase, 1 number, and 1 symbol.');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!validateForm()) return;

        setLoading(true);

        try {
            await authAPI.register({
                email: email.toLowerCase(),
                password: password,
                full_name: fullName.trim()
            });

            navigate('/login', { state: { message: 'Account created successfully! Please sign in.' } });
        } catch (err) {
            const errorDetail = err.response?.data?.detail;
            let errorMessage = 'Registration failed. Please try again.';

            if (typeof errorDetail === 'string') {
                errorMessage = errorDetail;
            } else if (Array.isArray(errorDetail)) {
                errorMessage = errorDetail[0].msg;
            }

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
                py: 4
            }}
        >
            <Container component="main" maxWidth="sm">
                <Paper
                    elevation={0}
                    sx={{
                        p: { xs: 4, md: 6 },
                        borderRadius: 4,
                        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.05), 0 8px 10px -6px rgb(0 0 0 / 0.01)',
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(10px)'
                    }}
                >
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
                        <Avatar sx={{ m: 1, bgcolor: 'secondary.main', width: 64, height: 64, boxShadow: '0 4px 14px 0 rgb(14 165 233 / 0.39)' }}>
                            <ScienceIcon fontSize="large" />
                        </Avatar>
                        <Typography component="h1" variant="h4" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                            Create an Account
                        </Typography>
                        <Typography variant="body1" color="text.secondary" align="center">
                            Start your drug discovery journey today.
                        </Typography>
                    </Box>

                    {error && <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>{error}</Alert>}

                    <Box component="form" onSubmit={handleSubmit} noValidate>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            label="Full Name"
                            autoFocus
                            value={fullName}
                            onChange={(e) => { setFullName(e.target.value); setError(''); }}
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            label="Email Address"
                            type="email"
                            value={email}
                            onChange={(e) => { setEmail(e.target.value); setError(''); }}
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            label="Password"
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => { setPassword(e.target.value); setError(''); }}
                            sx={{ mb: 3 }}
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
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            size="large"
                            disabled={loading}
                            sx={{
                                py: 1.5,
                                fontSize: '1.1rem',
                                boxShadow: '0 4px 6px -1px rgb(79 70 229 / 0.2)'
                            }}
                        >
                            {loading ? 'Creating account...' : 'Sign Up'}
                        </Button>

                        <Box sx={{ textAlign: 'center', mt: 4 }}>
                            <Typography variant="body2" color="text.secondary">
                                Already have an account?{' '}
                                <Link component={RouterLink} to="/login" sx={{ fontWeight: 600, textDecoration: 'none' }}>
                                    Sign In
                                </Link>
                            </Typography>
                        </Box>
                    </Box>
                </Paper>
            </Container>
        </Box>
    );
}