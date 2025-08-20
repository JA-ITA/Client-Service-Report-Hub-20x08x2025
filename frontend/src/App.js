import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Label } from "./components/ui/label";
import { Separator } from "./components/ui/separator";
import { Users, MapPin, Shield, CheckCircle, XCircle, Plus, FileText, Calendar, Save, Send, Edit, Trash2, Eye, BarChart3 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { username, password });
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      await axios.post(`${API}/auth/register`, userData);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAdmin: user?.role === 'ADMIN'
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(username, password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-slate-800">MonthlyReportsHub</CardTitle>
          <CardDescription>Sign in to your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <XCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter your username"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
          
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-600">
              Don't have an account?{' '}
              <button 
                onClick={() => navigate('/register')}
                className="text-blue-600 hover:underline font-medium"
              >
                Register here
              </button>
            </p>
          </div>
          
          <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-700 font-medium">Demo Credentials:</p>
            <p className="text-xs text-blue-600">Username: admin | Password: admin123</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    location_id: ''
  });
  const [locations, setLocations] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await axios.get(`${API}/locations`);
      setLocations(response.data);
    } catch (error) {
      console.error('Failed to fetch locations:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await register(formData);
    
    if (result.success) {
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-slate-800 mb-2">Registration Successful!</h2>
              <p className="text-slate-600">Your account has been created and is pending approval.</p>
              <p className="text-sm text-slate-500 mt-2">Redirecting to login...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-slate-800">Create Account</CardTitle>
          <CardDescription>Join MonthlyReportsHub</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <XCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
                placeholder="Choose a username"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                placeholder="Enter your email"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
                placeholder="Create a password"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="location">Location (Optional)</Label>
              <Select value={formData.location_id} onValueChange={(value) => setFormData({...formData, location_id: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a location" />
                </SelectTrigger>
                <SelectContent>
                  {locations.map((location) => (
                    <SelectItem key={location.id} value={location.id}>
                      {location.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Creating Account...' : 'Register'}
            </Button>
          </form>
          
          <div className="mt-4 text-center">
            <p className="text-sm text-slate-600">
              Already have an account?{' '}
              <button 
                onClick={() => navigate('/login')}
                className="text-blue-600 hover:underline font-medium"
              >
                Sign in here
              </button>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const Dashboard = () => {
  const { user, logout, isAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [locations, setLocations] = useState([]);
  const [stats, setStats] = useState({});
  const [reportTemplates, setReportTemplates] = useState([]);
  const [reports, setReports] = useState([]);
  const [editingLocation, setEditingLocation] = useState(null);
  const [newLocationName, setNewLocationName] = useState('');
  const [showAddLocation, setShowAddLocation] = useState(false);
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportFormData, setReportFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
      fetchLocations();
      fetchStats();
      fetchReportTemplates();
      fetchAllReports();
    } else {
      fetchReportTemplates();
      fetchUserReports();
    }
  }, [isAdmin]);

  // Fetch functions
  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      setError('Failed to fetch users');
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await axios.get(`${API}/admin/locations`);
      setLocations(response.data);
    } catch (error) {
      console.error('Failed to fetch locations:', error);
      setError('Failed to fetch locations');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchReportTemplates = async () => {
    try {
      const endpoint = isAdmin ? '/admin/report-templates' : '/report-templates';
      const response = await axios.get(`${API}${endpoint}`);
      setReportTemplates(response.data);
    } catch (error) {
      console.error('Failed to fetch report templates:', error);
      setError('Failed to fetch report templates');
    }
  };

  const fetchAllReports = async () => {
    try {
      const response = await axios.get(`${API}/admin/reports`);
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch all reports:', error);
      setError('Failed to fetch reports');
    }
  };

  const fetchUserReports = async () => {
    try {
      const response = await axios.get(`${API}/reports`);
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch user reports:', error);
      setError('Failed to fetch reports');
    }
  };

  // User and Location management functions (existing code stays)
  const approveUser = async (userId) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/approve`);
      fetchUsers();
      fetchStats();
    } catch (error) {
      console.error('Failed to approve user:', error);
      setError('Failed to approve user');
    }
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/role`, { role: newRole });
      fetchUsers();
      fetchStats();
    } catch (error) {
      console.error('Failed to update user role:', error);
      setError('Failed to update user role');
    }
  };

  const deleteUser = async (userId, username) => {
    if (window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
      try {
        await axios.delete(`${API}/admin/users/${userId}`);
        fetchUsers();
        fetchStats();
      } catch (error) {
        console.error('Failed to delete user:', error);
        setError(error.response?.data?.detail || 'Failed to delete user');
      }
    }
  };

  const addLocation = async () => {
    if (!newLocationName.trim()) return;
    
    setLoading(true);
    try {
      await axios.post(`${API}/locations`, { name: newLocationName });
      setNewLocationName('');
      setShowAddLocation(false);
      fetchLocations();
    } catch (error) {
      console.error('Failed to add location:', error);
      setError(error.response?.data?.detail || 'Failed to add location');
    } finally {
      setLoading(false);
    }
  };

  const updateLocation = async (locationId, newName) => {
    if (!newName.trim()) return;
    
    setLoading(true);
    try {
      await axios.put(`${API}/admin/locations/${locationId}`, { name: newName });
      setEditingLocation(null);
      fetchLocations();
    } catch (error) {
      console.error('Failed to update location:', error);
      setError(error.response?.data?.detail || 'Failed to update location');
    } finally {
      setLoading(false);
    }
  };

  const deleteLocation = async (locationId, locationName) => {
    if (window.confirm(`Are you sure you want to delete location "${locationName}"? This action cannot be undone.`)) {
      try {
        await axios.delete(`${API}/admin/locations/${locationId}`);
        fetchLocations();
      } catch (error) {
        console.error('Failed to delete location:', error);
        setError(error.response?.data?.detail || 'Failed to delete location');
      }
    }
  };

  // Report management functions
  const submitReport = async (templateId, reportPeriod, data, status = 'draft') => {
    setLoading(true);
    try {
      await axios.post(`${API}/reports`, {
        template_id: templateId,
        report_period: reportPeriod,
        data: data,
        status: status
      });
      
      if (isAdmin) {
        fetchAllReports();
      } else {
        fetchUserReports();
      }
      
      setReportFormData({});
      setSelectedReport(null);
    } catch (error) {
      console.error('Failed to submit report:', error);
      setError(error.response?.data?.detail || 'Failed to submit report');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentMonth = () => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const StatCard = ({ title, value, icon: Icon, color = "blue" }) => (
    <Card className="hover-lift">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-600">{title}</p>
            <p className={`text-3xl font-bold text-${color}-600`}>{value}</p>
          </div>
          <Icon className={`h-8 w-8 text-${color}-500 opacity-75`} />
        </div>
      </CardContent>
    </Card>
  );

  const ReportForm = ({ template, existingReport = null }) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileText className="h-5 w-5" />
          <span>{template.name}</span>
        </CardTitle>
        <CardDescription>{template.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {template.fields.sort((a, b) => a.order - b.order).map((field) => (
            <div key={field.id} className="space-y-2">
              <Label htmlFor={field.name}>
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </Label>
              
              {field.field_type === 'text' && (
                <Input
                  id={field.name}
                  placeholder={field.placeholder}
                  value={reportFormData[field.name] || existingReport?.data[field.name] || ''}
                  onChange={(e) => setReportFormData({
                    ...reportFormData,
                    [field.name]: e.target.value
                  })}
                  required={field.required}
                />
              )}
              
              {field.field_type === 'textarea' && (
                <textarea
                  id={field.name}
                  placeholder={field.placeholder}
                  className="w-full p-3 border border-slate-200 rounded-md resize-none h-24 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={reportFormData[field.name] || existingReport?.data[field.name] || ''}
                  onChange={(e) => setReportFormData({
                    ...reportFormData,
                    [field.name]: e.target.value
                  })}
                  required={field.required}
                />
              )}
              
              {field.field_type === 'number' && (
                <Input
                  id={field.name}
                  type="number"
                  placeholder={field.placeholder}
                  value={reportFormData[field.name] || existingReport?.data[field.name] || ''}
                  onChange={(e) => setReportFormData({
                    ...reportFormData,
                    [field.name]: e.target.value
                  })}
                  required={field.required}
                />
              )}
              
              {field.field_type === 'dropdown' && (
                <Select 
                  value={reportFormData[field.name] || existingReport?.data[field.name] || ''} 
                  onValueChange={(value) => setReportFormData({
                    ...reportFormData,
                    [field.name]: value
                  })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select an option" />
                  </SelectTrigger>
                  <SelectContent>
                    {field.options?.map((option) => (
                      <SelectItem key={option} value={option}>
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
          ))}
          
          <div className="flex space-x-4 pt-4">
            <Button 
              onClick={() => submitReport(template.id, getCurrentMonth(), reportFormData, 'draft')}
              variant="outline"
              disabled={loading}
            >
              <Save className="h-4 w-4 mr-2" />
              Save Draft
            </Button>
            <Button 
              onClick={() => submitReport(template.id, getCurrentMonth(), reportFormData, 'submitted')}
              disabled={loading}
            >
              <Send className="h-4 w-4 mr-2" />
              Submit Report
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setSelectedReport(null)}
            >
              Cancel
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <h1 className="text-xl font-bold text-slate-800">MonthlyReportsHub</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-slate-900">Welcome, {user?.username}!</p>
                <Badge variant={user?.role === 'ADMIN' ? 'default' : 'secondary'} className="text-xs">
                  {user?.role}
                </Badge>
              </div>
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Error Alert */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Alert className="border-red-200 bg-red-50">
            <XCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-700">
              {error}
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setError('')}
                className="ml-2 text-red-700 hover:text-red-900"
              >
                Dismiss
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-2">
            Welcome to MonthlyReportsHub
          </h2>
          <p className="text-slate-600">
            {isAdmin 
              ? "Manage users, locations, and system settings from your admin dashboard."
              : "Your account is active and you can access reporting features."
            }
          </p>
        </div>

        {isAdmin ? (
          <div className="space-y-8">
            {/* Statistics Dashboard */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard 
                title="Total Users" 
                value={stats.total_users || 0} 
                icon={Users} 
                color="blue" 
              />
              <StatCard 
                title="Pending Approvals" 
                value={stats.pending_users || 0} 
                icon={XCircle} 
                color="orange" 
              />
              <StatCard 
                title="Locations" 
                value={stats.total_locations || 0} 
                icon={MapPin} 
                color="green" 
              />
              <StatCard 
                title="Recent Signups" 
                value={stats.recent_registrations || 0} 
                icon={Plus} 
                color="purple" 
              />
            </div>

            <Tabs defaultValue="users" className="space-y-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="users" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>User Management</span>
                </TabsTrigger>
                <TabsTrigger value="locations" className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>Locations</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="users">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Users className="h-5 w-5" />
                        <span>User Management</span>
                      </div>
                      <Badge variant="outline">{users.length} users</Badge>
                    </CardTitle>
                    <CardDescription>
                      Manage user accounts, approvals, and roles
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {users.length === 0 ? (
                        <p className="text-slate-500 text-center py-8">No users found</p>
                      ) : (
                        users.map((userItem) => (
                          <div key={userItem.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover-lift">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <div>
                                  <p className="font-medium text-slate-900">{userItem.username}</p>
                                  <p className="text-sm text-slate-500">{userItem.email}</p>
                                  <p className="text-xs text-slate-400">
                                    Joined: {new Date(userItem.created_at).toLocaleDateString()}
                                  </p>
                                </div>
                                <div className="flex space-x-2">
                                  <Badge variant={userItem.role === 'ADMIN' ? 'default' : 'secondary'}>
                                    {userItem.role}
                                  </Badge>
                                  <Badge variant={userItem.approved ? 'default' : 'destructive'}>
                                    {userItem.approved ? 'Approved' : 'Pending'}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2 ml-4">
                              {!userItem.approved && userItem.role !== 'ADMIN' && (
                                <Button 
                                  size="sm" 
                                  onClick={() => approveUser(userItem.id)}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Approve
                                </Button>
                              )}
                              
                              {userItem.role === 'USER' && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => updateUserRole(userItem.id, 'ADMIN')}
                                >
                                  Make Admin
                                </Button>
                              )}
                              
                              {userItem.role === 'ADMIN' && userItem.id !== user.id && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => updateUserRole(userItem.id, 'USER')}
                                >
                                  Remove Admin
                                </Button>
                              )}
                              
                              {userItem.id !== user.id && (
                                <Button 
                                  size="sm" 
                                  variant="destructive"
                                  onClick={() => deleteUser(userItem.id, userItem.username)}
                                >
                                  <XCircle className="h-4 w-4" />
                                </Button>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="locations">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-5 w-5" />
                        <span>Location Management</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{locations.length} locations</Badge>
                        <Button 
                          size="sm" 
                          onClick={() => setShowAddLocation(true)}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          <Plus className="h-4 w-4 mr-1" />
                          Add Location
                        </Button>
                      </div>
                    </CardTitle>
                    <CardDescription>
                      Manage organization locations and assignments
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {/* Add Location Form */}
                    {showAddLocation && (
                      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Input
                            placeholder="Enter location name"
                            value={newLocationName}
                            onChange={(e) => setNewLocationName(e.target.value)}
                            className="flex-1"
                          />
                          <Button 
                            onClick={addLocation} 
                            disabled={loading || !newLocationName.trim()}
                          >
                            {loading ? 'Adding...' : 'Add'}
                          </Button>
                          <Button 
                            variant="outline" 
                            onClick={() => {
                              setShowAddLocation(false);
                              setNewLocationName('');
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}

                    <div className="space-y-4">
                      {locations.length === 0 ? (
                        <p className="text-slate-500 text-center py-8">No locations found</p>
                      ) : (
                        locations.map((location) => (
                          <div key={location.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover-lift">
                            <div className="flex-1">
                              {editingLocation === location.id ? (
                                <div className="flex items-center space-x-3">
                                  <Input
                                    defaultValue={location.name}
                                    onKeyPress={(e) => {
                                      if (e.key === 'Enter') {
                                        updateLocation(location.id, e.target.value);
                                      }
                                    }}
                                    onBlur={(e) => updateLocation(location.id, e.target.value)}
                                    className="flex-1"
                                    autoFocus
                                  />
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    onClick={() => setEditingLocation(null)}
                                  >
                                    Cancel
                                  </Button>
                                </div>
                              ) : (
                                <div>
                                  <p className="font-medium text-slate-900">{location.name}</p>
                                  <p className="text-sm text-slate-500">
                                    Created: {new Date(location.created_at).toLocaleDateString()}
                                  </p>
                                </div>
                              )}
                            </div>
                            
                            {editingLocation !== location.id && (
                              <div className="flex items-center space-x-2 ml-4">
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => setEditingLocation(location.id)}
                                >
                                  Edit
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="destructive"
                                  onClick={() => deleteLocation(location.id, location.name)}
                                >
                                  <XCircle className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>User Dashboard</CardTitle>
              <CardDescription>
                Welcome to your dashboard. Your account status and available features.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-slate-700">Account is approved and active</span>
                </div>
                
                <Separator />
                
                <div className="space-y-2">
                  <h3 className="font-medium text-slate-900">Account Information</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-slate-500">Username:</span>
                      <span className="ml-2 text-slate-900">{user?.username}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Email:</span>
                      <span className="ml-2 text-slate-900">{user?.email}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Role:</span>
                      <Badge className="ml-2" variant="secondary">{user?.role}</Badge>
                    </div>
                    <div>
                      <span className="text-slate-500">Status:</span>
                      <Badge className="ml-2" variant="default">Active</Badge>
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">Coming Soon</h4>
                  <p className="text-sm text-blue-700">
                    Monthly report submission features will be available in the next update. 
                    Stay tuned for dynamic form creation and report management capabilities!
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/login" replace />;
};

// Main App Component
function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;