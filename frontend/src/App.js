import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Shield, Users, MapPin, FileText, Settings, 
  CheckCircle, XCircle, Plus, Edit, Save, Send, 
  Eye, Calendar, BarChart3, Search, Filter, 
  Download, Upload, Trash2, RotateCcw, Copy,
  DragDropContext, Droppable, Draggable
} from 'lucide-react';

// UI Components (keeping existing ones and adding new ones)
const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-lg shadow-sm border border-slate-200 ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = "" }) => (
  <div className={`px-6 py-4 border-b border-slate-200 ${className}`}>
    {children}
  </div>
);

const CardContent = ({ children, className = "" }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
);

const CardTitle = ({ children, className = "" }) => (
  <h3 className={`text-lg font-semibold text-slate-900 ${className}`}>
    {children}
  </h3>
);

const CardDescription = ({ children, className = "" }) => (
  <p className={`text-sm text-slate-600 mt-1 ${className}`}>
    {children}
  </p>
);

const Button = ({ 
  children, 
  onClick, 
  type = "button", 
  variant = "primary", 
  size = "md",
  disabled = false,
  className = ""
}) => {
  const baseClasses = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200 focus:ring-slate-500",
    outline: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-slate-500",
    destructive: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
    ghost: "text-slate-700 hover:bg-slate-100 focus:ring-slate-500"
  };
  const sizes = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  };
  
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      {children}
    </button>
  );
};

const Input = ({ className = "", ...props }) => (
  <input
    className={`flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    {...props}
  />
);

const Label = ({ children, htmlFor, className = "" }) => (
  <label
    htmlFor={htmlFor}
    className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}
  >
    {children}
  </label>
);

const Select = ({ children, value, onValueChange, className = "" }) => {
  return (
    <select
      value={value}
      onChange={(e) => onValueChange(e.target.value)}
      className={`flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm ring-offset-white focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2 ${className}`}
    >
      {children}
    </select>
  );
};

const SelectTrigger = ({ children, className = "" }) => (
  <div className={className}>{children}</div>
);

const SelectValue = ({ placeholder }) => (
  <span className="text-slate-500">{placeholder}</span>
);

const SelectContent = ({ children }) => children;
const SelectItem = ({ children, value }) => (
  <option value={value}>{children}</option>
);

const Badge = ({ children, variant = "default", className = "" }) => {
  const variants = {
    default: "bg-slate-900 text-slate-50 hover:bg-slate-900/80",
    secondary: "bg-slate-100 text-slate-900 hover:bg-slate-100/80",
    destructive: "bg-red-500 text-slate-50 hover:bg-red-500/80",
    outline: "text-slate-950 border border-slate-200 bg-white hover:bg-slate-100"
  };
  
  return (
    <div className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2 ${variants[variant]} ${className}`}>
      {children}
    </div>
  );
};

const Alert = ({ children, className = "" }) => (
  <div className={`relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-slate-950 ${className}`}>
    {children}
  </div>
);

const AlertDescription = ({ children, className = "" }) => (
  <div className={`text-sm [&_p]:leading-relaxed ${className}`}>
    {children}
  </div>
);

const Tabs = ({ children, defaultValue, className = "", onValueChange }) => {
  const [activeTab, setActiveTab] = useState(defaultValue);
  
  const handleTabChange = (value) => {
    setActiveTab(value);
    if (onValueChange) onValueChange(value);
  };

  return (
    <div className={className}>
      {React.Children.map(children, child =>
        React.cloneElement(child, { activeTab, onTabChange: handleTabChange })
      )}
    </div>
  );
};

const TabsList = ({ children, className = "", activeTab, onTabChange }) => (
  <div className={`inline-flex h-10 items-center justify-center rounded-md bg-slate-100 p-1 text-slate-500 ${className}`}>
    {React.Children.map(children, child =>
      React.cloneElement(child, { activeTab, onTabChange })
    )}
  </div>
);

const TabsTrigger = ({ children, value, className = "", activeTab, onTabChange }) => (
  <button
    onClick={() => onTabChange(value)}
    className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
      activeTab === value 
        ? 'bg-white text-slate-950 shadow-sm' 
        : 'hover:bg-white/50'
    } ${className}`}
  >
    {children}
  </button>
);

const TabsContent = ({ children, value, className = "", activeTab }) => (
  activeTab === value ? (
    <div className={`mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 ${className}`}>
      {children}
    </div>
  ) : null
);

// Enhanced Modal Component
const Modal = ({ isOpen, onClose, title, children, size = "md" }) => {
  const sizes = {
    sm: "max-w-md",
    md: "max-w-lg", 
    lg: "max-w-2xl",
    xl: "max-w-4xl"
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
        <div className={`relative bg-white rounded-lg shadow-lg w-full ${sizes[size]}`}>
          <div className="flex items-center justify-between p-6 border-b">
            <h3 className="text-lg font-semibold">{title}</h3>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <XCircle className="h-4 w-4" />
            </Button>
          </div>
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

// Configuration
const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

// Configure axios defaults
axios.defaults.baseURL = API;

// Auth Context
const AuthContext = createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token with backend
      axios.get('/auth/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
          delete axios.defaults.headers.common['Authorization'];
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Login Component
const LoginForm = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/auth/login', formData);
      login(response.data.access_token, response.data.user);
      navigate('/dashboard');
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full">
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <CardTitle>MonthlyReportsHub</CardTitle>
            <CardDescription>Sign in to your account</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert className="mb-4 border-red-200 bg-red-50">
                <XCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>
              
              <Button 
                type="submit" 
                className="w-full"
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>
            
            <div className="mt-6 text-center">
              <p className="text-sm text-slate-600">
                Don't have an account?{' '}
                <button 
                  onClick={() => navigate('/register')}
                  className="text-blue-600 hover:underline"
                >
                  Register here
                </button>
              </p>
              
              <div className="mt-4 p-4 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-600 mb-2">Demo Credentials:</p>
                <p className="text-xs font-mono">Admin: admin / admin123</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Register Component
const RegisterForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    location_id: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState([]);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await axios.get('/locations');
      setLocations(response.data);
    } catch (error) {
      console.error('Failed to fetch locations:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post('/auth/register', formData);
      setSuccess(true);
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100">
        <Card className="max-w-md w-full">
          <CardContent className="text-center p-8">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <CardTitle className="mb-2">Registration Successful!</CardTitle>
            <CardDescription className="mb-6">
              Your account has been created and is pending approval. 
              You'll be able to log in once an administrator approves your account.
            </CardDescription>
            <Button onClick={() => navigate('/login')} className="w-full">
              Go to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full">
        <Card>
          <CardHeader className="text-center">
            <CardTitle>Create Account</CardTitle>
            <CardDescription>Register for MonthlyReportsHub</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert className="mb-4 border-red-200 bg-red-50">
                <XCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="location">Location</Label>
                <Select
                  value={formData.location_id}
                  onValueChange={(value) => setFormData({...formData, location_id: value})}
                >
                  <option value="">Select a location</option>
                  {locations.map(location => (
                    <option key={location.id} value={location.id}>
                      {location.name}
                    </option>
                  ))}
                </Select>
              </div>
              
              <Button 
                type="submit" 
                className="w-full"
                disabled={loading}
              >
                {loading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </form>
            
            <div className="mt-6 text-center">
              <p className="text-sm text-slate-600">
                Already have an account?{' '}
                <button 
                  onClick={() => navigate('/login')}
                  className="text-blue-600 hover:underline"
                >
                  Sign in here
                </button>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Enhanced Field Manager Component
const FieldManager = ({ 
  dynamicFields, 
  fieldSections, 
  onCreateField, 
  onUpdateField, 
  onDeleteField, 
  onRestoreField 
}) => {
  const [newFieldData, setNewFieldData] = useState({
    section: '',
    label: '',
    field_type: 'text',
    choices: [],
    placeholder: '',
    help_text: ''
  });
  const [editingField, setEditingField] = useState(null);
  const [choicesInput, setChoicesInput] = useState('');
  const [showDeleted, setShowDeleted] = useState(false);

  const fieldTypes = [
    { value: 'text', label: 'Text Input' },
    { value: 'textarea', label: 'Text Area' },
    { value: 'number', label: 'Number' },
    { value: 'date', label: 'Date' },
    { value: 'dropdown', label: 'Dropdown' },
    { value: 'multiselect', label: 'Multi-Select' },
    { value: 'checkbox', label: 'Checkbox' },
    { value: 'file', label: 'File Upload' }
  ];

  const handleCreateField = () => {
    const fieldData = { ...newFieldData };
    if (['dropdown', 'multiselect'].includes(fieldData.field_type)) {
      fieldData.choices = choicesInput.split('\n').filter(c => c.trim());
    }
    onCreateField(fieldData);
    resetForm();
  };

  const resetForm = () => {
    setNewFieldData({
      section: '',
      label: '',
      field_type: 'text',
      choices: [],
      placeholder: '',
      help_text: ''
    });
    setChoicesInput('');
  };

  const filteredFields = showDeleted 
    ? dynamicFields 
    : dynamicFields.filter(field => !field.deleted);

  const groupedFields = filteredFields.reduce((acc, field) => {
    if (!acc[field.section]) acc[field.section] = [];
    acc[field.section].push(field);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Field Creation Form */}
      <Card>
        <CardHeader>
          <CardTitle>Create New Field</CardTitle>
          <CardDescription>Add a new reusable field to the library</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="section">Section</Label>
              <Input
                id="section"
                value={newFieldData.section}
                onChange={(e) => setNewFieldData({...newFieldData, section: e.target.value})}
                placeholder="e.g., Basic Information"
              />
            </div>
            
            <div>
              <Label htmlFor="label">Field Label</Label>
              <Input
                id="label"
                value={newFieldData.label}
                onChange={(e) => setNewFieldData({...newFieldData, label: e.target.value})}
                placeholder="e.g., Employee Name"
              />
            </div>
            
            <div>
              <Label htmlFor="field_type">Field Type</Label>
              <Select
                value={newFieldData.field_type}
                onValueChange={(value) => setNewFieldData({...newFieldData, field_type: value})}
              >
                {fieldTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
            </div>
            
            <div>
              <Label htmlFor="placeholder">Placeholder Text</Label>
              <Input
                id="placeholder"
                value={newFieldData.placeholder}
                onChange={(e) => setNewFieldData({...newFieldData, placeholder: e.target.value})}
                placeholder="Optional placeholder text"
              />
            </div>
          </div>

          {['dropdown', 'multiselect'].includes(newFieldData.field_type) && (
            <div className="mt-4">
              <Label htmlFor="choices">Choices (one per line)</Label>
              <textarea
                id="choices"
                value={choicesInput}
                onChange={(e) => setChoicesInput(e.target.value)}
                className="w-full p-3 border border-slate-200 rounded-md resize-none h-24"
                placeholder="Option 1\nOption 2\nOption 3"
              />
            </div>
          )}

          <div className="mt-4">
            <Label htmlFor="help_text">Help Text</Label>
            <Input
              id="help_text"
              value={newFieldData.help_text}
              onChange={(e) => setNewFieldData({...newFieldData, help_text: e.target.value})}
              placeholder="Optional help text for users"
            />
          </div>

          <div className="mt-6 flex space-x-4">
            <Button onClick={handleCreateField}>
              <Plus className="h-4 w-4 mr-2" />
              Create Field
            </Button>
            <Button variant="outline" onClick={resetForm}>
              Reset
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Fields Library */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Field Library</CardTitle>
              <CardDescription>Manage reusable fields organized by section</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDeleted(!showDeleted)}
              >
                {showDeleted ? 'Hide Deleted' : 'Show Deleted'}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {Object.keys(groupedFields).length === 0 ? (
            <p className="text-slate-500 text-center py-8">No fields found</p>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedFields).map(([section, fields]) => (
                <div key={section}>
                  <h4 className="font-medium text-slate-900 mb-3 pb-2 border-b">
                    {section}
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {fields.map(field => (
                      <Card key={field.id} className={`${field.deleted ? 'bg-red-50 border-red-200' : 'hover:shadow-md transition-shadow'}`}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <h5 className="font-medium text-slate-900">{field.label}</h5>
                                <Badge variant="outline" className="text-xs">
                                  {field.field_type}
                                </Badge>
                                {field.deleted && (
                                  <Badge variant="destructive" className="text-xs">
                                    Deleted
                                  </Badge>
                                )}
                              </div>
                              {field.placeholder && (
                                <p className="text-xs text-slate-500 mt-1">
                                  Placeholder: {field.placeholder}
                                </p>
                              )}
                              {field.help_text && (
                                <p className="text-xs text-slate-600 mt-1">
                                  Help: {field.help_text}
                                </p>
                              )}
                              {field.choices && field.choices.length > 0 && (
                                <p className="text-xs text-slate-500 mt-1">
                                  Options: {field.choices.slice(0, 3).join(', ')}{field.choices.length > 3 ? '...' : ''}
                                </p>
                              )}
                            </div>
                            <div className="flex space-x-1 ml-2">
                              {field.deleted ? (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => onRestoreField(field.id)}
                                >
                                  <RotateCcw className="h-3 w-3" />
                                </Button>
                              ) : (
                                <>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setEditingField(field)}
                                  >
                                    <Edit className="h-3 w-3" />
                                  </Button>
                                  <Button
                                    variant="destructive"
                                    size="sm"
                                    onClick={() => onDeleteField(field.id, field.label)}
                                  >
                                    <Trash2 className="h-3 w-3" />
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Enhanced Template Builder Component
const TemplateBuilder = ({ 
  dynamicFields, 
  onCreateTemplate 
}) => {
  const [templateData, setTemplateData] = useState({
    name: '',
    description: '',
    category: 'General'
  });
  const [selectedFields, setSelectedFields] = useState([]);
  const [previewHtml, setPreviewHtml] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  const groupedFields = dynamicFields
    .filter(field => !field.deleted)
    .reduce((acc, field) => {
      if (!acc[field.section]) acc[field.section] = [];
      acc[field.section].push(field);
      return acc;
    }, {});

  const handleFieldToggle = (field) => {
    const isSelected = selectedFields.some(f => f.id === field.id);
    if (isSelected) {
      setSelectedFields(selectedFields.filter(f => f.id !== field.id));
    } else {
      setSelectedFields([...selectedFields, field]);
    }
  };

  const generatePreview = async () => {
    if (!templateData.name || selectedFields.length === 0) {
      alert('Please enter template name and select at least one field');
      return;
    }

    try {
      const response = await axios.post('/admin/report-templates/preview', {
        ...templateData,
        fields: selectedFields
      });
      setPreviewHtml(response.data.preview_html);
      setShowPreview(true);
    } catch (error) {
      console.error('Failed to generate preview:', error);
    }
  };

  const handleCreateTemplate = async () => {
    if (!templateData.name || selectedFields.length === 0) {
      alert('Please enter template name and select at least one field');
      return;
    }

    try {
      await axios.post('/admin/report-templates/from-fields', {
        template_name: templateData.name,
        template_description: templateData.description,
        field_ids: selectedFields.map(f => f.id),
        template_category: templateData.category
      });
      
      // Reset form
      setTemplateData({ name: '', description: '', category: 'General' });
      setSelectedFields([]);
      setShowPreview(false);
      onCreateTemplate();
    } catch (error) {
      console.error('Failed to create template:', error);
      alert(error.response?.data?.detail || 'Failed to create template');
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Template Builder</CardTitle>
          <CardDescription>Create report templates from your field library</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <Label htmlFor="template_name">Template Name</Label>
              <Input
                id="template_name"
                value={templateData.name}
                onChange={(e) => setTemplateData({...templateData, name: e.target.value})}
                placeholder="e.g., Monthly Performance Review"
              />
            </div>
            
            <div>
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                value={templateData.category}
                onChange={(e) => setTemplateData({...templateData, category: e.target.value})}
                placeholder="e.g., HR, Operations"
              />
            </div>
          </div>

          <div className="mb-6">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              value={templateData.description}
              onChange={(e) => setTemplateData({...templateData, description: e.target.value})}
              className="w-full p-3 border border-slate-200 rounded-md resize-none h-20"
              placeholder="Describe the purpose of this template..."
            />
          </div>

          {/* Field Selection */}
          <div className="space-y-4">
            <h4 className="font-medium text-slate-900">Select Fields</h4>
            {Object.keys(groupedFields).length === 0 ? (
              <p className="text-slate-500">No fields available. Create some fields first.</p>
            ) : (
              <div className="space-y-4">
                {Object.entries(groupedFields).map(([section, fields]) => (
                  <div key={section}>
                    <h5 className="font-medium text-slate-700 mb-2">{section}</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {fields.map(field => (
                        <label key={field.id} className="flex items-center space-x-2 p-2 border rounded cursor-pointer hover:bg-slate-50">
                          <input
                            type="checkbox"
                            checked={selectedFields.some(f => f.id === field.id)}
                            onChange={() => handleFieldToggle(field)}
                            className="rounded"
                          />
                          <div className="flex-1">
                            <span className="text-sm font-medium">{field.label}</span>
                            <Badge variant="outline" className="ml-2 text-xs">
                              {field.field_type}
                            </Badge>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedFields.length > 0 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800 mb-2">
                Selected Fields ({selectedFields.length}):
              </p>
              <div className="flex flex-wrap gap-1">
                {selectedFields.map(field => (
                  <Badge key={field.id} variant="default" className="text-xs">
                    {field.label}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 flex space-x-4">
            <Button onClick={generatePreview}>
              <Eye className="h-4 w-4 mr-2" />
              Preview Template
            </Button>
            <Button onClick={handleCreateTemplate} variant="outline">
              <Save className="h-4 w-4 mr-2" />
              Create Template
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Preview Modal */}
      <Modal 
        isOpen={showPreview} 
        onClose={() => setShowPreview(false)}
        title={`Preview: ${templateData.name}`}
        size="lg"
      >
        <div 
          className="preview-content"
          dangerouslySetInnerHTML={{ __html: previewHtml }}
        />
      </Modal>
    </div>
  );
};

// Enhanced Reports Management Component with Search and Filtering
const ReportsManager = ({ 
  reports, 
  reportTemplates, 
  users, 
  locations, 
  onSearch, 
  onBulkAction, 
  onExport 
}) => {
  const [searchFilters, setSearchFilters] = useState({
    search_term: '',
    status: '',
    template_id: '',
    user_id: '',
    location_id: '',
    date_from: '',
    date_to: ''
  });
  const [selectedReports, setSelectedReports] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = () => {
    onSearch(searchFilters);
  };

  const handleSelectAll = () => {
    if (selectedReports.length === reports.length) {
      setSelectedReports([]);
    } else {
      setSelectedReports(reports.map(r => r.id));
    }
  };

  const handleBulkAction = (action) => {
    if (selectedReports.length === 0) {
      alert('Please select reports first');
      return;
    }
    
    if (window.confirm(`Are you sure you want to ${action} ${selectedReports.length} reports?`)) {
      onBulkAction(action, selectedReports);
      setSelectedReports([]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Advanced Report Management</CardTitle>
              <CardDescription>Search, filter, and manage report submissions</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
              <Button
                variant="outline" 
                size="sm"
                onClick={() => onExport(searchFilters)}
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex-1">
              <Input
                placeholder="Search reports..."
                value={searchFilters.search_term}
                onChange={(e) => setSearchFilters({...searchFilters, search_term: e.target.value})}
              />
            </div>
            <Button onClick={handleSearch}>
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 p-4 bg-slate-50 rounded-lg">
              <div>
                <Label>Status</Label>
                <Select
                  value={searchFilters.status}
                  onValueChange={(value) => setSearchFilters({...searchFilters, status: value})}
                >
                  <option value="">All Status</option>
                  <option value="draft">Draft</option>
                  <option value="submitted">Submitted</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </Select>
              </div>

              <div>
                <Label>Template</Label>
                <Select
                  value={searchFilters.template_id}
                  onValueChange={(value) => setSearchFilters({...searchFilters, template_id: value})}
                >
                  <option value="">All Templates</option>
                  {reportTemplates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <Label>User</Label>
                <Select
                  value={searchFilters.user_id}
                  onValueChange={(value) => setSearchFilters({...searchFilters, user_id: value})}
                >
                  <option value="">All Users</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>
                      {user.username}
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <Label>From Date</Label>
                <Input
                  type="date"
                  value={searchFilters.date_from}
                  onChange={(e) => setSearchFilters({...searchFilters, date_from: e.target.value})}
                />
              </div>

              <div>
                <Label>To Date</Label>
                <Input
                  type="date"
                  value={searchFilters.date_to}
                  onChange={(e) => setSearchFilters({...searchFilters, date_to: e.target.value})}
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedReports.length > 0 && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-blue-800">
                {selectedReports.length} reports selected
              </span>
              <div className="flex space-x-2">
                <Button size="sm" onClick={() => handleBulkAction('approve')}>
                  Approve
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleBulkAction('reject')}>
                  Reject
                </Button>
                <Button size="sm" variant="destructive" onClick={() => handleBulkAction('delete')}>
                  Delete
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reports Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Reports ({reports.length})</CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
            >
              {selectedReports.length === reports.length ? 'Deselect All' : 'Select All'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {reports.length === 0 ? (
            <p className="text-slate-500 text-center py-8">No reports found</p>
          ) : (
            <div className="space-y-2">
              {reports.map(report => (
                <div key={report.id} className="flex items-center space-x-4 p-4 border border-slate-200 rounded-lg hover:bg-slate-50">
                  <input
                    type="checkbox"
                    checked={selectedReports.includes(report.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedReports([...selectedReports, report.id]);
                      } else {
                        setSelectedReports(selectedReports.filter(id => id !== report.id));
                      }
                    }}
                    className="rounded"
                  />
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div>
                        <p className="font-medium text-slate-900">{report.template_name}</p>
                        <p className="text-sm text-slate-500">
                          By: {report.username} • Period: {report.report_period}
                        </p>
                        <p className="text-xs text-slate-400">
                          {report.location_name && `Location: ${report.location_name} • `}
                          Submitted: {report.submitted_at ? new Date(report.submitted_at).toLocaleDateString() : 'Draft'}
                        </p>
                      </div>
                      <Badge variant={
                        report.status === 'submitted' ? 'default' : 
                        report.status === 'approved' ? 'default' :
                        report.status === 'rejected' ? 'destructive' :
                        report.status === 'draft' ? 'secondary' : 'outline'
                      }>
                        {report.status}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => {
                        alert(`Report Data: ${JSON.stringify(report.data, null, 2)}`);
                      }}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Enhanced Dashboard with Analytics
const EnhancedAnalyticsDashboard = ({ analytics }) => {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Users</p>
                <p className="text-3xl font-bold text-blue-600">{analytics.total_users || 0}</p>
                <p className="text-xs text-slate-500 mt-1">
                  Approval Rate: {analytics.approval_rate || 0}%
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-500 opacity-75" />
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Reports</p>
                <p className="text-3xl font-bold text-green-600">{analytics.total_reports || 0}</p>
                <p className="text-xs text-slate-500 mt-1">
                  Submission Rate: {analytics.submission_rate || 0}%
                </p>
              </div>
              <FileText className="h-8 w-8 text-green-500 opacity-75" />
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Dynamic Fields</p>
                <p className="text-3xl font-bold text-purple-600">{analytics.total_fields || 0}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {analytics.field_sections?.length || 0} sections
                </p>
              </div>
              <Settings className="h-8 w-8 text-purple-500 opacity-75" />
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Recent Activity</p>
                <p className="text-3xl font-bold text-orange-600">{analytics.recent_submissions || 0}</p>
                <p className="text-xs text-slate-500 mt-1">
                  Last 7 days
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-orange-500 opacity-75" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Field Sections Breakdown */}
      {analytics.section_stats && Object.keys(analytics.section_stats).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Field Distribution by Section</CardTitle>
            <CardDescription>Number of fields in each section</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(analytics.section_stats).map(([section, count]) => (
                <div key={section} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <span className="font-medium text-slate-700">{section}</span>
                  <Badge variant="outline">{count} fields</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Activity Timeline */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Report Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Draft Reports</span>
                <Badge variant="secondary">{analytics.draft_reports || 0}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Submitted Reports</span>
                <Badge variant="default">{analytics.submitted_reports || 0}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Monthly Submissions</span>
                <Badge variant="outline">{analytics.monthly_submissions || 0}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Active Templates</span>
                <Badge variant="outline">{analytics.total_templates || 0}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Total Locations</span>
                <Badge variant="outline">{analytics.total_locations || 0}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Recent Registrations</span>
                <Badge variant="outline">{analytics.recent_registrations || 0}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Main Enhanced Dashboard Component
const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === 'ADMIN';

  // State management (existing + new)
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [users, setUsers] = useState([]);
  const [locations, setLocations] = useState([]);
  const [stats, setStats] = useState({});
  const [analytics, setAnalytics] = useState({});
  const [reports, setReports] = useState([]);
  const [reportTemplates, setReportTemplates] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportFormData, setReportFormData] = useState({});

  // Enhanced Stage 3 state
  const [dynamicFields, setDynamicFields] = useState([]);
  const [fieldSections, setFieldSections] = useState([]);
  const [showFieldManager, setShowFieldManager] = useState(false);
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');

  // Existing location management state
  const [newLocationName, setNewLocationName] = useState('');
  const [showAddLocation, setShowAddLocation] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);

  // Enhanced field management state
  const [newFieldData, setNewFieldData] = useState({
    section: '',
    label: '',
    field_type: 'text',
    choices: [],
    placeholder: '',
    help_text: ''
  });

  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
      fetchLocations();
      fetchStats();
      fetchAnalytics();
      fetchAllReports();
      fetchDynamicFields();
      fetchFieldSections();
    } else {
      fetchUserReports();
    }
    fetchReportTemplates();
  }, [isAdmin]);

  // Fetch functions (existing + enhanced)
  const fetchUsers = async () => {
    try {
      const response = await axios.get('/admin/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      setError('Failed to fetch users');
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await axios.get('/admin/locations');
      setLocations(response.data);
    } catch (error) {
      console.error('Failed to fetch locations:', error);
      setError('Failed to fetch locations');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/admin/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('/admin/analytics');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchReportTemplates = async () => {
    try {
      const endpoint = isAdmin ? '/admin/report-templates' : '/report-templates';
      const response = await axios.get(endpoint);
      setReportTemplates(response.data);
    } catch (error) {
      console.error('Failed to fetch report templates:', error);
      setError('Failed to fetch report templates');
    }
  };

  const fetchAllReports = async () => {
    try {
      const response = await axios.get('/admin/reports');
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch all reports:', error);
      setError('Failed to fetch reports');
    }
  };

  const fetchUserReports = async () => {
    try {
      const response = await axios.get('/reports');
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch user reports:', error);
      setError('Failed to fetch reports');
    }
  };

  const fetchDynamicFields = async () => {
    try {
      const response = await axios.get('/admin/dynamic-fields?include_deleted=true');
      setDynamicFields(response.data);
    } catch (error) {
      console.error('Failed to fetch dynamic fields:', error);
      setError('Failed to fetch dynamic fields');
    }
  };

  const fetchFieldSections = async () => {
    try {
      const response = await axios.get('/admin/dynamic-fields/sections');
      setFieldSections(response.data.sections);
    } catch (error) {
      console.error('Failed to fetch field sections:', error);
    }
  };

  // Enhanced management functions
  const createDynamicField = async (fieldData) => {
    setLoading(true);
    try {
      await axios.post('/admin/dynamic-fields', fieldData);
      fetchDynamicFields();
      fetchFieldSections();
      setShowFieldManager(false);
    } catch (error) {
      console.error('Failed to create dynamic field:', error);
      setError(error.response?.data?.detail || 'Failed to create dynamic field');
    } finally {
      setLoading(false);
    }
  };

  const deleteDynamicField = async (fieldId, fieldLabel) => {
    if (window.confirm(`Are you sure you want to delete field "${fieldLabel}"? This action can be undone.`)) {
      try {
        await axios.delete(`/admin/dynamic-fields/${fieldId}`);
        fetchDynamicFields();
      } catch (error) {
        console.error('Failed to delete dynamic field:', error);
        setError(error.response?.data?.detail || 'Failed to delete dynamic field');
      }
    }
  };

  const restoreDynamicField = async (fieldId) => {
    try {
      await axios.post(`/admin/dynamic-fields/${fieldId}/restore`);
      fetchDynamicFields();
    } catch (error) {
      console.error('Failed to restore dynamic field:', error);
      setError(error.response?.data?.detail || 'Failed to restore dynamic field');
    }
  };

  const searchReports = async (filters) => {
    try {
      const params = new URLSearchParams(filters).toString();
      const response = await axios.get(`/admin/reports/search?${params}`);
      setReports(response.data.reports);
    } catch (error) {
      console.error('Failed to search reports:', error);
      setError('Failed to search reports');
    }
  };

  const handleBulkAction = async (action, reportIds) => {
    try {
      await axios.post('/admin/reports/bulk-actions', {
        action,
        report_ids: reportIds
      });
      fetchAllReports();
    } catch (error) {
      console.error('Failed to perform bulk action:', error);
      setError(error.response?.data?.detail || 'Failed to perform bulk action');
    }
  };

  const handleExport = async (filters) => {
    try {
      const params = new URLSearchParams({...filters, format: 'csv'}).toString();
      const response = await axios.get(`/admin/reports/export?${params}`);
      
      // For now, just show the export data - in production you'd trigger download
      alert(`Export ready: ${response.data.filename}\nRecords: ${response.data.data.length}`);
    } catch (error) {
      console.error('Failed to export reports:', error);
      setError('Failed to export reports');
    }
  };

  // Existing functions (keeping all the existing user management, location management, etc.)
  const approveUser = async (userId) => {
    try {
      await axios.put(`/admin/users/${userId}/approve`);
      fetchUsers();
      fetchStats();
    } catch (error) {
      console.error('Failed to approve user:', error);
      setError('Failed to approve user');
    }
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      await axios.put(`/admin/users/${userId}/role`, { role: newRole });
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
        await axios.delete(`/admin/users/${userId}`);
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
      await axios.post('/locations', { name: newLocationName });
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
      await axios.put(`/admin/locations/${locationId}`, { name: newName });
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
        await axios.delete(`/admin/locations/${locationId}`);
        fetchLocations();
      } catch (error) {
        console.error('Failed to delete location:', error);
        setError(error.response?.data?.detail || 'Failed to delete location');
      }
    }
  };

  const submitReport = async (templateId, reportPeriod, data, status = 'draft') => {
    setLoading(true);
    try {
      await axios.post('/reports', {
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

  // Enhanced navigation
  const handleNavigation = (page) => {
    setCurrentPage(page);
    setError(''); // Clear any errors when navigating
  };

  const StatCard = ({ title, value, icon: Icon, color = "blue" }) => (
    <Card className="hover:shadow-md transition-shadow">
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

              {field.field_type === 'date' && (
                <Input
                  id={field.name}
                  type="date"
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
                  <option value="">Select an option</option>
                  {field.options?.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </Select>
              )}

              {field.field_type === 'checkbox' && (
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={field.name}
                    checked={reportFormData[field.name] || existingReport?.data[field.name] || false}
                    onChange={(e) => setReportFormData({
                      ...reportFormData,
                      [field.name]: e.target.checked
                    })}
                    className="rounded"
                  />
                  <Label htmlFor={field.name}>{field.label}</Label>
                </div>
              )}

              {field.field_type === 'file' && (
                <Input
                  id={field.name}
                  type="file"
                  onChange={(e) => {
                    // For now, just store the filename
                    // In production, you'd upload the file and store the URL
                    setReportFormData({
                      ...reportFormData,
                      [field.name]: e.target.files[0]?.name || ''
                    });
                  }}
                />
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
              ? "Enhanced admin dashboard with advanced field management and analytics."
              : "Your account is active and you can access reporting features."
            }
          </p>
        </div>

        {isAdmin ? (
          <div className="space-y-8">
            {/* Enhanced Admin Navigation */}
            <div className="flex flex-wrap gap-2 mb-6">
              <Button
                variant={currentPage === 'dashboard' ? 'default' : 'outline'}
                onClick={() => handleNavigation('dashboard')}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Analytics
              </Button>
              <Button
                variant={currentPage === 'users' ? 'default' : 'outline'}
                onClick={() => handleNavigation('users')}
              >
                <Users className="h-4 w-4 mr-2" />
                Users
              </Button>
              <Button
                variant={currentPage === 'locations' ? 'default' : 'outline'}
                onClick={() => handleNavigation('locations')}
              >
                <MapPin className="h-4 w-4 mr-2" />
                Locations
              </Button>
              <Button
                variant={currentPage === 'fields' ? 'default' : 'outline'}
                onClick={() => handleNavigation('fields')}
              >
                <Settings className="h-4 w-4 mr-2" />
                Field Library
              </Button>
              <Button
                variant={currentPage === 'templates' ? 'default' : 'outline'}
                onClick={() => handleNavigation('templates')}
              >
                <Copy className="h-4 w-4 mr-2" />
                Template Builder
              </Button>
              <Button
                variant={currentPage === 'reports' ? 'default' : 'outline'}
                onClick={() => handleNavigation('reports')}
              >
                <FileText className="h-4 w-4 mr-2" />
                Advanced Reports
              </Button>
            </div>

            {/* Enhanced Analytics Dashboard */}
            {currentPage === 'dashboard' && (
              <EnhancedAnalyticsDashboard analytics={analytics} />
            )}

            {/* Field Management */}
            {currentPage === 'fields' && (
              <FieldManager
                dynamicFields={dynamicFields}
                fieldSections={fieldSections}
                onCreateField={createDynamicField}
                onUpdateField={() => fetchDynamicFields()}
                onDeleteField={deleteDynamicField}
                onRestoreField={restoreDynamicField}
              />
            )}

            {/* Template Builder */}
            {currentPage === 'templates' && (
              <TemplateBuilder
                dynamicFields={dynamicFields}
                onCreateTemplate={fetchReportTemplates}
              />
            )}

            {/* Advanced Reports Management */}
            {currentPage === 'reports' && (
              <ReportsManager
                reports={reports}
                reportTemplates={reportTemplates}
                users={users}
                locations={locations}
                onSearch={searchReports}
                onBulkAction={handleBulkAction}
                onExport={handleExport}
              />
            )}

            {/* Existing tabs for users and locations */}
            {(currentPage === 'users' || currentPage === 'locations') && (
              <Tabs defaultValue={currentPage} className="space-y-6">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger 
                    value="users" 
                    className="flex items-center space-x-2"
                    onClick={() => handleNavigation('users')}
                  >
                    <Users className="h-4 w-4" />
                    <span>Users</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="locations" 
                    className="flex items-center space-x-2"
                    onClick={() => handleNavigation('locations')}
                  >
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
                            <div key={userItem.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:shadow-md transition-shadow">
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
                            <div key={location.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:shadow-md transition-shadow">
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
            )}
          </div>
        ) : (
          // User Dashboard (keeping existing functionality)
          <div className="space-y-8">
            {/* User Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard 
                title="My Reports" 
                value={reports.length || 0} 
                icon={FileText} 
                color="blue" 
              />
              <StatCard 
                title="This Month" 
                value={reports.filter(r => r.report_period === getCurrentMonth()).length || 0} 
                icon={Calendar} 
                color="green" 
              />
              <StatCard 
                title="Templates" 
                value={reportTemplates.length || 0} 
                icon={BarChart3} 
                color="purple" 
              />
            </div>

            {/* Report Form or List */}
            {selectedReport ? (
              <ReportForm 
                template={reportTemplates.find(t => t.id === selectedReport)} 
                existingReport={reports.find(r => 
                  r.template_id === selectedReport && 
                  r.report_period === getCurrentMonth()
                )}
              />
            ) : (
              <div className="space-y-6">
                {/* Available Templates */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <FileText className="h-5 w-5" />
                      <span>Create New Report</span>
                    </CardTitle>
                    <CardDescription>
                      Select a report template to create your monthly report for {getCurrentMonth()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {reportTemplates.map((template) => (
                        <Card key={template.id} className="cursor-pointer hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <h3 className="font-medium text-slate-900">{template.name}</h3>
                                <p className="text-sm text-slate-500 mt-1">{template.description}</p>
                                <p className="text-xs text-slate-400 mt-2">
                                  {template.fields.length} fields
                                </p>
                              </div>
                              <Button 
                                size="sm"
                                onClick={() => setSelectedReport(template.id)}
                              >
                                Start Report
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* My Reports History */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5" />
                      <span>My Reports</span>
                    </CardTitle>
                    <CardDescription>
                      Your report submission history
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {reports.length === 0 ? (
                        <p className="text-slate-500 text-center py-8">No reports submitted yet</p>
                      ) : (
                        reports.map((report) => (
                          <div key={report.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg hover:shadow-md transition-shadow">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <div>
                                  <p className="font-medium text-slate-900">{report.template_name}</p>
                                  <p className="text-sm text-slate-500">Period: {report.report_period}</p>
                                  <p className="text-xs text-slate-400">
                                    {report.submitted_at ? `Submitted: ${new Date(report.submitted_at).toLocaleDateString()}` : 'Draft'}
                                  </p>
                                </div>
                                <Badge variant={
                                  report.status === 'submitted' ? 'default' : 
                                  report.status === 'approved' ? 'default' :
                                  report.status === 'rejected' ? 'destructive' :
                                  report.status === 'draft' ? 'secondary' : 'outline'
                                }>
                                  {report.status}
                                </Badge>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2 ml-4">
                              {report.status === 'draft' && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => setSelectedReport(report.template_id)}
                                >
                                  <Edit className="h-4 w-4 mr-1" />
                                  Edit
                                </Button>
                              )}
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => {
                                  alert(`Report Data: ${JSON.stringify(report.data, null, 2)}`);
                                }}
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

// Protected Route Component (keeping existing)
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

// Main App Component (keeping existing)
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