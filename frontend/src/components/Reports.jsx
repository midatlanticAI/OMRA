import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  ButtonGroup,
  CircularProgress,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tab,
  Tabs,
  Stack
} from '@mui/material';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import {
  FileDownload as DownloadIcon,
  Print as PrintIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

// Mock data for reports
const mockRevenueData = [
  { month: 'Jan', income: 22500, expenses: 18000, profit: 4500 },
  { month: 'Feb', income: 26000, expenses: 20800, profit: 5200 },
  { month: 'Mar', income: 25500, expenses: 20600, profit: 4900 },
  { month: 'Apr', income: 29000, expenses: 22900, profit: 6100 },
  { month: 'May', income: 27800, expenses: 22000, profit: 5800 },
  { month: 'Jun', income: 31200, expenses: 24100, profit: 7100 },
  { month: 'Jul', income: 33500, expenses: 25200, profit: 8300 }
];

const mockServiceTypeData = [
  { name: 'Refrigerator', value: 35 },
  { name: 'Washing Machine', value: 25 },
  { name: 'Dryer', value: 15 },
  { name: 'Dishwasher', value: 12 },
  { name: 'Oven/Stove', value: 8 },
  { name: 'Other', value: 5 }
];

const mockTechnicianPerformance = [
  { name: 'Sarah Johnson', completed: 28, inProgress: 4, satisfaction: 4.8 },
  { name: 'Michael Rodriguez', completed: 32, inProgress: 3, satisfaction: 4.6 },
  { name: 'David Wilson', completed: 24, inProgress: 5, satisfaction: 4.7 }
];

const mockAppointmentsData = [
  { month: 'Jan', scheduled: 45, completed: 42, cancelled: 3 },
  { month: 'Feb', scheduled: 48, completed: 45, cancelled: 3 },
  { month: 'Mar', scheduled: 52, completed: 48, cancelled: 4 },
  { month: 'Apr', scheduled: 58, completed: 55, cancelled: 3 },
  { month: 'May', scheduled: 62, completed: 58, cancelled: 4 },
  { month: 'Jun', scheduled: 65, completed: 61, cancelled: 4 },
  { month: 'Jul', scheduled: 68, completed: 65, cancelled: 3 }
];

const mockTopCustomers = [
  { id: 1, name: 'John Doe', totalSpent: 2850, serviceCount: 5, lastService: '2023-04-25' },
  { id: 2, name: 'Emily Wilson', totalSpent: 2200, serviceCount: 4, lastService: '2023-05-10' },
  { id: 3, name: 'Robert Johnson', totalSpent: 1950, serviceCount: 3, lastService: '2023-03-15' },
  { id: 4, name: 'Sarah Parker', totalSpent: 1800, serviceCount: 3, lastService: '2023-05-05' },
  { id: 5, name: 'Michael Brown', totalSpent: 1650, serviceCount: 3, lastService: '2023-02-20' }
];

// Colors for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28CFF', '#FF6B6B'];

// Report component
const Reports = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dateRange, setDateRange] = useState('year');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Handle date range change
  const handleDateRangeChange = (event) => {
    setDateRange(event.target.value);
    
    // Reset custom dates when switching to predefined ranges
    if (event.target.value !== 'custom') {
      setStartDate(null);
      setEndDate(null);
    }
  };

  // Generate report based on filters
  const handleGenerateReport = () => {
    setLoading(true);
    // In a real app, this would fetch the data based on the date range
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  // Export report as CSV
  const handleExportCSV = () => {
    // In a real app, this would generate and download a CSV file
    alert('Exporting report as CSV...');
  };

  // Print report
  const handlePrintReport = () => {
    // In a real app, this would open the print dialog
    window.print();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Reports & Analytics
        </Typography>

        {/* Report Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
          >
            <Tab label="Financial" />
            <Tab label="Service" />
            <Tab label="Technician" />
            <Tab label="Customer" />
          </Tabs>
        </Paper>

        {/* Filter Controls */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel id="date-range-label">Date Range</InputLabel>
                <Select
                  labelId="date-range-label"
                  value={dateRange}
                  label="Date Range"
                  onChange={handleDateRangeChange}
                >
                  <MenuItem value="month">This Month</MenuItem>
                  <MenuItem value="quarter">This Quarter</MenuItem>
                  <MenuItem value="year">This Year</MenuItem>
                  <MenuItem value="custom">Custom Range</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {dateRange === 'custom' && (
              <>
                <Grid item xs={12} sm={3}>
                  <DatePicker
                    label="Start Date"
                    value={startDate}
                    onChange={(newValue) => setStartDate(newValue)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Grid>
                <Grid item xs={12} sm={3}>
                  <DatePicker
                    label="End Date"
                    value={endDate}
                    onChange={(newValue) => setEndDate(newValue)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                    minDate={startDate}
                  />
                </Grid>
              </>
            )}

            <Grid item xs={12} sm={dateRange === 'custom' ? 3 : 9} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <ButtonGroup variant="contained">
                <Button 
                  startIcon={<FilterIcon />}
                  onClick={handleGenerateReport}
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Generate Report'}
                </Button>
                <Button 
                  startIcon={<DownloadIcon />}
                  onClick={handleExportCSV}
                >
                  Export
                </Button>
                <Button 
                  startIcon={<PrintIcon />}
                  onClick={handlePrintReport}
                >
                  Print
                </Button>
              </ButtonGroup>
            </Grid>
          </Grid>
        </Paper>

        {/* Report Content based on active tab */}
        {loading ? (
          <Box display="flex" justifyContent="center" p={5}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {/* Financial Reports */}
            {activeTab === 0 && (
              <Grid container spacing={3}>
                {/* Summary Cards */}
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Total Revenue</Typography>
                      <Typography variant="h3" color="primary">
                        ${mockRevenueData.reduce((sum, item) => sum + item.income, 0).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Year to date
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Total Expenses</Typography>
                      <Typography variant="h3" color="error">
                        ${mockRevenueData.reduce((sum, item) => sum + item.expenses, 0).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Year to date
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Net Profit</Typography>
                      <Typography variant="h3" color="success.main">
                        ${mockRevenueData.reduce((sum, item) => sum + item.profit, 0).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Year to date
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Revenue Chart */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Revenue vs Expenses</Typography>
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart
                        data={mockRevenueData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip 
                          formatter={(value) => ['$' + value.toLocaleString(), '']}
                          labelFormatter={(label) => `Month: ${label}`}
                        />
                        <Legend />
                        <Bar dataKey="income" name="Revenue" fill="#0088FE" />
                        <Bar dataKey="expenses" name="Expenses" fill="#FF8042" />
                        <Bar dataKey="profit" name="Profit" fill="#00C49F" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>
              </Grid>
            )}

            {/* Service Reports */}
            {activeTab === 1 && (
              <Grid container spacing={3}>
                {/* Summary Cards */}
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Total Services</Typography>
                      <Typography variant="h3" color="primary">
                        {mockAppointmentsData.reduce((sum, item) => sum + item.completed, 0)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Completed this year
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Average Service Value</Typography>
                      <Typography variant="h3" color="primary">
                        $421
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Per completed service
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Cancellation Rate</Typography>
                      <Typography variant="h3" color="primary">
                        5.8%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Year to date
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Service Type Distribution */}
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Service Type Distribution</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={mockServiceTypeData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        >
                          {mockServiceTypeData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value} services`, 'Count']} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>

                {/* Appointment Trends */}
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Appointment Trends</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart
                        data={mockAppointmentsData}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="scheduled" name="Scheduled" stroke="#0088FE" activeDot={{ r: 8 }} />
                        <Line type="monotone" dataKey="completed" name="Completed" stroke="#00C49F" />
                        <Line type="monotone" dataKey="cancelled" name="Cancelled" stroke="#FF8042" />
                      </LineChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>
              </Grid>
            )}

            {/* Technician Reports */}
            {activeTab === 2 && (
              <Grid container spacing={3}>
                {/* Technician Performance Table */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Technician Performance</Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell align="right">Completed Jobs</TableCell>
                            <TableCell align="right">In Progress</TableCell>
                            <TableCell align="right">Customer Satisfaction</TableCell>
                            <TableCell align="right">Efficiency Rate</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {mockTechnicianPerformance.map((tech) => (
                            <TableRow key={tech.name}>
                              <TableCell component="th" scope="row">
                                {tech.name}
                              </TableCell>
                              <TableCell align="right">{tech.completed}</TableCell>
                              <TableCell align="right">{tech.inProgress}</TableCell>
                              <TableCell align="right">{tech.satisfaction} / 5.0</TableCell>
                              <TableCell align="right">
                                {((tech.completed / (tech.completed + tech.inProgress)) * 100).toFixed(1)}%
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>
                </Grid>

                {/* Technician Workload */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Technician Workload</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={mockTechnicianPerformance}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="completed" name="Completed Jobs" fill="#00C49F" />
                        <Bar dataKey="inProgress" name="In Progress" fill="#0088FE" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>
              </Grid>
            )}

            {/* Customer Reports */}
            {activeTab === 3 && (
              <Grid container spacing={3}>
                {/* Top Customer Stats */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Top Customers by Revenue</Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Customer Name</TableCell>
                            <TableCell align="right">Total Spent</TableCell>
                            <TableCell align="right">Service Count</TableCell>
                            <TableCell align="right">Avg. Service Value</TableCell>
                            <TableCell>Last Service Date</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {mockTopCustomers.map((customer) => (
                            <TableRow key={customer.id}>
                              <TableCell component="th" scope="row">
                                {customer.name}
                              </TableCell>
                              <TableCell align="right">${customer.totalSpent.toLocaleString()}</TableCell>
                              <TableCell align="right">{customer.serviceCount}</TableCell>
                              <TableCell align="right">
                                ${(customer.totalSpent / customer.serviceCount).toFixed(2)}
                              </TableCell>
                              <TableCell>
                                {new Date(customer.lastService).toLocaleDateString()}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>
                </Grid>

                {/* Customer Service Value Chart */}
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Customer Revenue Distribution</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={mockTopCustomers}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value) => ['$' + value.toLocaleString(), '']} />
                        <Legend />
                        <Bar dataKey="totalSpent" name="Total Spent" fill="#8884d8" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Paper>
                </Grid>
              </Grid>
            )}
          </>
        )}
      </Box>
    </LocalizationProvider>
  );
};

export default Reports; 