import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { format, subDays, startOfDay, endOfDay, parseISO } from 'date-fns';
import { de } from 'date-fns/locale';

interface StatsData {
  total_posts: number;
  total_likes: number;
  total_comments: number;
  total_follows: number;
  total_connections: number;
  engagement_rate: number;
  growth_rate: number;
  top_hashtags: { hashtag: string; count: number }[];
  post_performance: {
    id: number;
    title: string;
    likes: number;
    comments: number;
    shares: number;
    views: number;
    engagement_rate: number;
    published_at: string;
  }[];
  daily_stats: {
    date: string;
    likes: number;
    comments: number;
    follows: number;
    connections: number;
  }[];
  interaction_types: {
    type: string;
    count: number;
  }[];
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`stats-tabpanel-${index}`}
      aria-labelledby={`stats-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Statistics: React.FC = () => {
  const [statsData, setStatsData] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [timeRange, setTimeRange] = useState<string>('7d');
  const [tabValue, setTabValue] = useState<number>(0);

  useEffect(() => {
    fetchStats();
  }, [timeRange]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/stats?time_range=${timeRange}`);
      if (!response.ok) {
        throw new Error('Fehler beim Laden der Statistiken');
      }
      const data = await response.json();
      setStatsData(data);
      setError('');
    } catch (err) {
      setError('Fehler beim Laden der Statistiken');
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setTimeRange(event.target.value as string);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const formatDate = (dateString: string) => {
    return format(parseISO(dateString), 'dd.MM.yyyy', { locale: de });
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('de-DE').format(num);
  };

  const formatPercentage = (num: number) => {
    return `${(num * 100).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!statsData) {
    return null;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            LinkedIn Statistiken
          </Typography>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Zeitraum</InputLabel>
            <Select
              value={timeRange}
              onChange={handleTimeRangeChange}
              label="Zeitraum"
            >
              <MenuItem value="7d">Letzte 7 Tage</MenuItem>
              <MenuItem value="30d">Letzte 30 Tage</MenuItem>
              <MenuItem value="90d">Letzte 90 Tage</MenuItem>
              <MenuItem value="all">Gesamt</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Übersichtskarten */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Beiträge
                </Typography>
                <Typography variant="h4">
                  {formatNumber(statsData.total_posts)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Engagement-Rate
                </Typography>
                <Typography variant="h4">
                  {formatPercentage(statsData.engagement_rate)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Wachstumsrate
                </Typography>
                <Typography variant="h4">
                  {formatPercentage(statsData.growth_rate)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Interaktionen
                </Typography>
                <Typography variant="h4">
                  {formatNumber(statsData.total_likes + statsData.total_comments)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="stats tabs">
            <Tab label="Übersicht" />
            <Tab label="Beiträge" />
            <Tab label="Interaktionen" />
            <Tab label="Hashtags" />
          </Tabs>
        </Box>

        {/* Übersicht-Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Tägliche Interaktionen
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={statsData.daily_stats}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis />
                    <Tooltip labelFormatter={formatDate} />
                    <Legend />
                    <Line type="monotone" dataKey="likes" name="Likes" stroke="#8884d8" />
                    <Line type="monotone" dataKey="comments" name="Kommentare" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="follows" name="Folgen" stroke="#ffc658" />
                    <Line type="monotone" dataKey="connections" name="Verbindungen" stroke="#ff7300" />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Interaktionstypen
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statsData.interaction_types}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                      nameKey="type"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {statsData.interaction_types.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatNumber(value as number)} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Beiträge-Tab */}
        <TabPanel value={tabValue} index={1}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Beitrags-Performance
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={statsData.post_performance}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="title" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="likes" name="Likes" fill="#8884d8" />
                <Bar dataKey="comments" name="Kommentare" fill="#82ca9d" />
                <Bar dataKey="shares" name="Shares" fill="#ffc658" />
                <Bar dataKey="views" name="Aufrufe" fill="#ff7300" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </TabPanel>

        {/* Interaktionen-Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Interaktionen pro Tag
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={statsData.daily_stats}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis />
                    <Tooltip labelFormatter={formatDate} />
                    <Legend />
                    <Bar dataKey="likes" name="Likes" fill="#8884d8" />
                    <Bar dataKey="comments" name="Kommentare" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Verbindungen pro Tag
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={statsData.daily_stats}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis />
                    <Tooltip labelFormatter={formatDate} />
                    <Legend />
                    <Bar dataKey="follows" name="Folgen" fill="#ffc658" />
                    <Bar dataKey="connections" name="Verbindungen" fill="#ff7300" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Hashtags-Tab */}
        <TabPanel value={tabValue} index={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Hashtags
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={statsData.top_hashtags}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="hashtag" type="category" width={80} />
                <Tooltip formatter={(value) => formatNumber(value as number)} />
                <Legend />
                <Bar dataKey="count" name="Verwendung" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default Statistics; 