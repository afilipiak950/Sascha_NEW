import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  CircularProgress,
  Box,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';

interface Settings {
  linkedin_email: string;
  linkedin_password: string;
  openai_api_key: string;
  post_generation_frequency: string;
  daily_connection_limit: number;
  interaction_interval: number;
  auto_publish_posts: boolean;
  auto_approve_comments: boolean;
  target_keywords: string[];
  excluded_keywords: string[];
  target_industries: string[];
  target_locations: string[];
  target_company_sizes: string[];
  target_titles: string[];
  target_seniority_levels: string[];
  interaction_types: string[];
  post_topics: string[];
  post_tones: string[];
  post_lengths: string[];
  post_hashtags: string[];
  comment_templates: string[];
  connection_message_templates: string[];
  follow_up_message_templates: string[];
  notification_settings: {
    email_notifications: boolean;
    slack_notifications: boolean;
    slack_webhook_url: string;
  };
  proxy_settings: {
    use_proxy: boolean;
    proxy_url: string;
    proxy_username: string;
    proxy_password: string;
  };
  browser_settings: {
    headless: boolean;
    user_agent: string;
    viewport_width: number;
    viewport_height: number;
  };
  rate_limiting: {
    max_requests_per_hour: number;
    max_connections_per_day: number;
    max_interactions_per_day: number;
    max_messages_per_day: number;
  };
}

const validationSchema = yup.object({
  linkedin_email: yup.string().email('Ungültige E-Mail-Adresse').required('E-Mail ist erforderlich'),
  linkedin_password: yup.string().required('Passwort ist erforderlich'),
  openai_api_key: yup.string().required('API-Key ist erforderlich'),
  post_generation_frequency: yup.string().required('Beitragsgenerierungshäufigkeit ist erforderlich'),
  daily_connection_limit: yup.number().min(1).max(50).required(),
  interaction_interval: yup.number().min(1).max(24).required(),
});

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showProxyPassword, setShowProxyPassword] = useState<boolean>(false);
  const [newKeyword, setNewKeyword] = useState<string>('');
  const [newTemplate, setNewTemplate] = useState<string>('');

  const formik = useFormik<Settings>({
    initialValues: {
      linkedin_email: '',
      linkedin_password: '',
      openai_api_key: '',
      post_generation_frequency: 'daily',
      daily_connection_limit: 39,
      interaction_interval: 4,
      auto_publish_posts: false,
      auto_approve_comments: false,
      target_keywords: [],
      excluded_keywords: [],
      target_industries: [],
      target_locations: [],
      target_company_sizes: [],
      target_titles: [],
      target_seniority_levels: [],
      interaction_types: [],
      post_topics: [],
      post_tones: [],
      post_lengths: [],
      post_hashtags: [],
      comment_templates: [],
      connection_message_templates: [],
      follow_up_message_templates: [],
      notification_settings: {
        email_notifications: false,
        slack_notifications: false,
        slack_webhook_url: '',
      },
      proxy_settings: {
        use_proxy: false,
        proxy_url: '',
        proxy_username: '',
        proxy_password: '',
      },
      browser_settings: {
        headless: true,
        user_agent: '',
        viewport_width: 1920,
        viewport_height: 1080,
      },
      rate_limiting: {
        max_requests_per_hour: 1000,
        max_connections_per_day: 100,
        max_interactions_per_day: 500,
        max_messages_per_day: 50,
      },
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/v1/settings', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(values),
        });

        if (response.ok) {
          setSuccess('Einstellungen erfolgreich gespeichert');
          setError('');
        } else {
          throw new Error('Fehler beim Speichern der Einstellungen');
        }
      } catch (err) {
        setError('Fehler beim Speichern der Einstellungen');
        setSuccess('');
      } finally {
        setLoading(false);
      }
    },
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/settings');
      if (!response.ok) {
        throw new Error('Fehler beim Laden der Einstellungen');
      }
      const data = await response.json();
      setSettings(data);
      setError('');
    } catch (err) {
      setError('Fehler beim Laden der Einstellungen');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    if (settings) {
      setSettings({
        ...settings,
        [field]: value,
      });
    }
  };

  const handleNestedInputChange = (parent: string, field: string, value: any) => {
    if (settings) {
      setSettings({
        ...settings,
        [parent]: {
          ...settings[parent as keyof Settings],
          [field]: value,
        },
      });
    }
  };

  const handleSaveSettings = async () => {
    if (!settings) return;

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (!response.ok) {
        throw new Error('Fehler beim Speichern der Einstellungen');
      }

      const updatedSettings = await response.json();
      setSettings(updatedSettings);
      setSuccess('Einstellungen erfolgreich gespeichert');
      setError('');
    } catch (err) {
      setError('Fehler beim Speichern der Einstellungen');
    } finally {
      setLoading(false);
    }
  };

  const handleAddKeyword = (type: 'target' | 'excluded') => {
    if (!newKeyword.trim()) return;
    
    const field = `keywords.${type}`;
    const currentKeywords = formik.values.keywords[type];
    
    if (!currentKeywords.includes(newKeyword)) {
      formik.setFieldValue(field, [...currentKeywords, newKeyword]);
    }
    
    setNewKeyword('');
  };

  const handleRemoveKeyword = (type: 'target' | 'excluded', keyword: string) => {
    const field = `keywords.${type}`;
    const currentKeywords = formik.values.keywords[type];
    formik.setFieldValue(
      field,
      currentKeywords.filter((k: string) => k !== keyword)
    );
  };

  const handleAddTemplate = (type: 'comment' | 'connection' | 'follow_up') => {
    if (!newTemplate.trim() || !settings) return;

    const field = `${type}_message_templates`;
    if (!settings[field as keyof Settings].includes(newTemplate)) {
      handleInputChange(field, [...settings[field as keyof Settings], newTemplate]);
    }
    setNewTemplate('');
  };

  const handleRemoveTemplate = (type: 'comment' | 'connection' | 'follow_up', template: string) => {
    if (!settings) return;

    const field = `${type}_message_templates`;
    handleInputChange(
      field,
      settings[field as keyof Settings].filter((t) => t !== template)
    );
  };

  const handleTestConnection = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/settings/test-connection', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Fehler bei der Verbindungstestung');
      }

      setSuccess('Verbindungstest erfolgreich');
      setError('');
    } catch (err) {
      setError('Fehler bei der Verbindungstestung');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !settings) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error && !settings) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!settings) {
    return null;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            LinkedIn Einstellungen
          </Typography>
          <Box>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={handleTestConnection}
              sx={{ mr: 2 }}
            >
              Verbindung testen
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SaveIcon />}
              onClick={handleSaveSettings}
              disabled={loading}
            >
              Speichern
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* LinkedIn Anmeldedaten */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  LinkedIn Anmeldedaten
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="E-Mail"
                      value={settings.linkedin_email}
                      onChange={(e) => handleInputChange('linkedin_email', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Passwort"
                      type={showPassword ? 'text' : 'password'}
                      value={settings.linkedin_password}
                      onChange={(e) => handleInputChange('linkedin_password', e.target.value)}
                      InputProps={{
                        endAdornment: (
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                          >
                            {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        ),
                      }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* OpenAI API */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  OpenAI API
                </Typography>
                <TextField
                  fullWidth
                  label="API-Schlüssel"
                  type="password"
                  value={settings.openai_api_key}
                  onChange={(e) => handleInputChange('openai_api_key', e.target.value)}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Automatisierungseinstellungen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Automatisierungseinstellungen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Beitragsgenerierungshäufigkeit</InputLabel>
                      <Select
                        value={settings.post_generation_frequency}
                        onChange={(e) => handleInputChange('post_generation_frequency', e.target.value)}
                        label="Beitragsgenerierungshäufigkeit"
                      >
                        <MenuItem value="daily">Täglich</MenuItem>
                        <MenuItem value="weekly">Wöchentlich</MenuItem>
                        <MenuItem value="biweekly">Zweiwöchentlich</MenuItem>
                        <MenuItem value="monthly">Monatlich</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Tägliches Verbindungslimit"
                      type="number"
                      value={settings.daily_connection_limit}
                      onChange={(e) => handleInputChange('daily_connection_limit', parseInt(e.target.value))}
                      InputProps={{ inputProps: { min: 1, max: 100 } }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Interaktionsintervall (Stunden)"
                      type="number"
                      value={settings.interaction_interval}
                      onChange={(e) => handleInputChange('interaction_interval', parseInt(e.target.value))}
                      InputProps={{ inputProps: { min: 1, max: 24 } }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.auto_publish_posts}
                          onChange={(e) => handleInputChange('auto_publish_posts', e.target.checked)}
                        />
                      }
                      label="Beiträge automatisch veröffentlichen"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.auto_approve_comments}
                          onChange={(e) => handleInputChange('auto_approve_comments', e.target.checked)}
                        />
                      }
                      label="Kommentare automatisch genehmigen"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Zielgruppen-Einstellungen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Zielgruppen-Einstellungen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Zielindustrien</InputLabel>
                      <Select
                        multiple
                        value={settings.target_industries}
                        onChange={(e) => handleInputChange('target_industries', e.target.value)}
                        label="Zielindustrien"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="technology">Technologie</MenuItem>
                        <MenuItem value="finance">Finanzen</MenuItem>
                        <MenuItem value="healthcare">Gesundheitswesen</MenuItem>
                        <MenuItem value="education">Bildung</MenuItem>
                        <MenuItem value="manufacturing">Fertigung</MenuItem>
                        <MenuItem value="retail">Einzelhandel</MenuItem>
                        <MenuItem value="consulting">Beratung</MenuItem>
                        <MenuItem value="marketing">Marketing</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Zielstandorte</InputLabel>
                      <Select
                        multiple
                        value={settings.target_locations}
                        onChange={(e) => handleInputChange('target_locations', e.target.value)}
                        label="Zielstandorte"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="germany">Deutschland</MenuItem>
                        <MenuItem value="austria">Österreich</MenuItem>
                        <MenuItem value="switzerland">Schweiz</MenuItem>
                        <MenuItem value="united_states">Vereinigte Staaten</MenuItem>
                        <MenuItem value="united_kingdom">Großbritannien</MenuItem>
                        <MenuItem value="france">Frankreich</MenuItem>
                        <MenuItem value="italy">Italien</MenuItem>
                        <MenuItem value="spain">Spanien</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Unternehmensgrößen</InputLabel>
                      <Select
                        multiple
                        value={settings.target_company_sizes}
                        onChange={(e) => handleInputChange('target_company_sizes', e.target.value)}
                        label="Unternehmensgrößen"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="1-10">1-10 Mitarbeiter</MenuItem>
                        <MenuItem value="11-50">11-50 Mitarbeiter</MenuItem>
                        <MenuItem value="51-200">51-200 Mitarbeiter</MenuItem>
                        <MenuItem value="201-500">201-500 Mitarbeiter</MenuItem>
                        <MenuItem value="501-1000">501-1000 Mitarbeiter</MenuItem>
                        <MenuItem value="1001-5000">1001-5000 Mitarbeiter</MenuItem>
                        <MenuItem value="5001-10000">5001-10000 Mitarbeiter</MenuItem>
                        <MenuItem value="10001+">Über 10000 Mitarbeiter</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Zielpositionen</InputLabel>
                      <Select
                        multiple
                        value={settings.target_titles}
                        onChange={(e) => handleInputChange('target_titles', e.target.value)}
                        label="Zielpositionen"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="ceo">CEO</MenuItem>
                        <MenuItem value="cto">CTO</MenuItem>
                        <MenuItem value="cmo">CMO</MenuItem>
                        <MenuItem value="cfo">CFO</MenuItem>
                        <MenuItem value="manager">Manager</MenuItem>
                        <MenuItem value="director">Direktor</MenuItem>
                        <MenuItem value="vp">Vizepräsident</MenuItem>
                        <MenuItem value="head">Head of</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Senioritätsstufen</InputLabel>
                      <Select
                        multiple
                        value={settings.target_seniority_levels}
                        onChange={(e) => handleInputChange('target_seniority_levels', e.target.value)}
                        label="Senioritätsstufen"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="entry">Einstieg</MenuItem>
                        <MenuItem value="associate">Associate</MenuItem>
                        <MenuItem value="mid">Mittelstufe</MenuItem>
                        <MenuItem value="senior">Senior</MenuItem>
                        <MenuItem value="lead">Lead</MenuItem>
                        <MenuItem value="manager">Manager</MenuItem>
                        <MenuItem value="director">Direktor</MenuItem>
                        <MenuItem value="vp">Vizepräsident</MenuItem>
                        <MenuItem value="cxo">C-Level</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Schlüsselwörter */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Schlüsselwörter
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Ziel-Schlüsselwörter
                    </Typography>
                    <Box sx={{ display: 'flex', mb: 2 }}>
                      <TextField
                        fullWidth
                        label="Neues Schlüsselwort"
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleAddKeyword('target');
                          }
                        }}
                      />
                      <Button
                        variant="contained"
                        onClick={() => handleAddKeyword('target')}
                        sx={{ ml: 1 }}
                      >
                        <AddIcon />
                      </Button>
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {settings.target_keywords.map((keyword) => (
                        <Chip
                          key={keyword}
                          label={keyword}
                          onDelete={() => handleRemoveKeyword('target', keyword)}
                        />
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>
                      Ausgeschlossene Schlüsselwörter
                    </Typography>
                    <Box sx={{ display: 'flex', mb: 2 }}>
                      <TextField
                        fullWidth
                        label="Neues Schlüsselwort"
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleAddKeyword('excluded');
                          }
                        }}
                      />
                      <Button
                        variant="contained"
                        onClick={() => handleAddKeyword('excluded')}
                        sx={{ ml: 1 }}
                      >
                        <AddIcon />
                      </Button>
                    </Box>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {settings.excluded_keywords.map((keyword) => (
                        <Chip
                          key={keyword}
                          label={keyword}
                          onDelete={() => handleRemoveKeyword('excluded', keyword)}
                        />
                      ))}
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Interaktionstypen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Interaktionstypen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          name="interaction_types.likes"
                          checked={formik.values.interaction_types.likes}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Likes"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          name="interaction_types.comments"
                          checked={formik.values.interaction_types.comments}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Kommentare"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          name="interaction_types.follows"
                          checked={formik.values.interaction_types.follows}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Folgen"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          name="interaction_types.connection_requests"
                          checked={formik.values.interaction_types.connection_requests}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Verbindungsanfragen"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          name="interaction_types.messages"
                          checked={formik.values.interaction_types.messages}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Nachrichten"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          name="interaction_types.shares"
                          checked={formik.values.interaction_types.shares}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Teilen"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Beitragseinstellungen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Beitragseinstellungen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Beitragsthemen</InputLabel>
                      <Select
                        multiple
                        value={formik.values.post_settings.topics}
                        onChange={formik.handleChange}
                        name="post_settings.topics"
                        label="Beitragsthemen"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="industry_news">Branchennachrichten</MenuItem>
                        <MenuItem value="company_updates">Unternehmensupdates</MenuItem>
                        <MenuItem value="product_launches">Produkteinführungen</MenuItem>
                        <MenuItem value="thought_leadership">Thought Leadership</MenuItem>
                        <MenuItem value="case_studies">Fallstudien</MenuItem>
                        <MenuItem value="tips_tricks">Tipps & Tricks</MenuItem>
                        <MenuItem value="events">Veranstaltungen</MenuItem>
                        <MenuItem value="job_openings">Stellenangebote</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Beitragstöne</InputLabel>
                      <Select
                        multiple
                        value={formik.values.post_settings.tones}
                        onChange={formik.handleChange}
                        name="post_settings.tones"
                        label="Beitragstöne"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="professional">Professionell</MenuItem>
                        <MenuItem value="casual">Lässig</MenuItem>
                        <MenuItem value="enthusiastic">Begeistert</MenuItem>
                        <MenuItem value="informative">Informativ</MenuItem>
                        <MenuItem value="humorous">Humorvoll</MenuItem>
                        <MenuItem value="inspirational">Inspirierend</MenuItem>
                        <MenuItem value="educational">Lehrreich</MenuItem>
                        <MenuItem value="conversational">Konversationell</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Beitragslängen</InputLabel>
                      <Select
                        multiple
                        value={formik.values.post_settings.lengths}
                        onChange={formik.handleChange}
                        name="post_settings.lengths"
                        label="Beitragslängen"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="short">Kurz (1-2 Absätze)</MenuItem>
                        <MenuItem value="medium">Mittel (3-4 Absätze)</MenuItem>
                        <MenuItem value="long">Lang (5+ Absätze)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Beitrags-Hashtags</InputLabel>
                      <Select
                        multiple
                        value={formik.values.post_settings.hashtags}
                        onChange={formik.handleChange}
                        name="post_settings.hashtags"
                        label="Beitrags-Hashtags"
                        renderValue={(selected) => (selected as string[]).join(', ')}
                      >
                        <MenuItem value="#innovation">#Innovation</MenuItem>
                        <MenuItem value="#technology">#Technology</MenuItem>
                        <MenuItem value="#leadership">#Leadership</MenuItem>
                        <MenuItem value="#marketing">#Marketing</MenuItem>
                        <MenuItem value="#sales">#Sales</MenuItem>
                        <MenuItem value="#entrepreneurship">#Entrepreneurship</MenuItem>
                        <MenuItem value="#startup">#Startup</MenuItem>
                        <MenuItem value="#digital">#Digital</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Nachrichtenvorlagen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Nachrichtenvorlagen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1" gutterBottom>
                      Kommentarvorlagen
                    </Typography>
                    <Box sx={{ display: 'flex', mb: 2 }}>
                      <TextField
                        fullWidth
                        label="Neue Vorlage"
                        value={newTemplate}
                        onChange={(e) => setNewTemplate(e.target.value)}
                        multiline
                        rows={2}
                      />
                      <Button
                        variant="contained"
                        onClick={() => handleAddTemplate('comment')}
                        sx={{ ml: 1 }}
                      >
                        <AddIcon />
                      </Button>
                    </Box>
                    <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                      {formik.values.message_templates.comments.map((template, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" sx={{ flexGrow: 1 }}>
                            {template}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveTemplate('comment', template)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1" gutterBottom>
                      Verbindungsnachrichten
                    </Typography>
                    <Box sx={{ display: 'flex', mb: 2 }}>
                      <TextField
                        fullWidth
                        label="Neue Vorlage"
                        value={newTemplate}
                        onChange={(e) => setNewTemplate(e.target.value)}
                        multiline
                        rows={2}
                      />
                      <Button
                        variant="contained"
                        onClick={() => handleAddTemplate('connection')}
                        sx={{ ml: 1 }}
                      >
                        <AddIcon />
                      </Button>
                    </Box>
                    <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                      {formik.values.message_templates.connection_messages.map((template, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" sx={{ flexGrow: 1 }}>
                            {template}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveTemplate('connection', template)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1" gutterBottom>
                      Follow-Up-Nachrichten
                    </Typography>
                    <Box sx={{ display: 'flex', mb: 2 }}>
                      <TextField
                        fullWidth
                        label="Neue Vorlage"
                        value={newTemplate}
                        onChange={(e) => setNewTemplate(e.target.value)}
                        multiline
                        rows={2}
                      />
                      <Button
                        variant="contained"
                        onClick={() => handleAddTemplate('follow_up')}
                        sx={{ ml: 1 }}
                      >
                        <AddIcon />
                      </Button>
                    </Box>
                    <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                      {formik.values.message_templates.follow_ups.map((template, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" sx={{ flexGrow: 1 }}>
                            {template}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveTemplate('follow_up', template)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      ))}
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Benachrichtigungseinstellungen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Benachrichtigungseinstellungen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formik.values.notification_settings.email_notifications}
                          onChange={formik.handleChange}
                          name="notification_settings.email_notifications"
                        />
                      }
                      label="E-Mail-Benachrichtigungen"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formik.values.notification_settings.slack_notifications}
                          onChange={formik.handleChange}
                          name="notification_settings.slack_notifications"
                        />
                      }
                      label="Slack-Benachrichtigungen"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Slack Webhook URL"
                      name="notification_settings.slack_webhook_url"
                      value={formik.values.notification_settings.slack_webhook_url}
                      onChange={formik.handleChange}
                      error={formik.touched.notification_settings?.slack_webhook_url && Boolean(formik.errors.notification_settings?.slack_webhook_url)}
                      helperText={formik.touched.notification_settings?.slack_webhook_url && formik.errors.notification_settings?.slack_webhook_url}
                      disabled={!formik.values.notification_settings.slack_notifications}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Proxy-Einstellungen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Proxy-Einstellungen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formik.values.proxy_settings.use_proxy}
                          onChange={formik.handleChange}
                          name="proxy_settings.use_proxy"
                        />
                      }
                      label="Proxy verwenden"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Proxy URL"
                      name="proxy_settings.proxy_url"
                      value={formik.values.proxy_settings.proxy_url}
                      onChange={formik.handleChange}
                      error={formik.touched.proxy_settings?.proxy_url && Boolean(formik.errors.proxy_settings?.proxy_url)}
                      helperText={formik.touched.proxy_settings?.proxy_url && formik.errors.proxy_settings?.proxy_url}
                      disabled={!formik.values.proxy_settings.use_proxy}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Proxy Benutzername"
                      name="proxy_settings.proxy_username"
                      value={formik.values.proxy_settings.proxy_username}
                      onChange={formik.handleChange}
                      error={formik.touched.proxy_settings?.proxy_username && Boolean(formik.errors.proxy_settings?.proxy_username)}
                      helperText={formik.touched.proxy_settings?.proxy_username && formik.errors.proxy_settings?.proxy_username}
                      disabled={!formik.values.proxy_settings.use_proxy}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Proxy Passwort"
                      name="proxy_settings.proxy_password"
                      type={showPassword ? 'text' : 'password'}
                      value={formik.values.proxy_settings.proxy_password}
                      onChange={formik.handleChange}
                      error={formik.touched.proxy_settings?.proxy_password && Boolean(formik.errors.proxy_settings?.proxy_password)}
                      helperText={formik.touched.proxy_settings?.proxy_password && formik.errors.proxy_settings?.proxy_password}
                      disabled={!formik.values.proxy_settings.use_proxy}
                      InputProps={{
                        endAdornment: (
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                          >
                            {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        ),
                      }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Browser-Einstellungen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Browser-Einstellungen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formik.values.browser_settings.headless}
                          onChange={formik.handleChange}
                          name="browser_settings.headless"
                        />
                      }
                      label="Headless-Modus"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="User Agent"
                      name="browser_settings.user_agent"
                      value={formik.values.browser_settings.user_agent}
                      onChange={formik.handleChange}
                      error={formik.touched.browser_settings?.user_agent && Boolean(formik.errors.browser_settings?.user_agent)}
                      helperText={formik.touched.browser_settings?.user_agent && formik.errors.browser_settings?.user_agent}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Viewport Breite"
                      name="browser_settings.viewport_width"
                      type="number"
                      value={formik.values.browser_settings.viewport_width}
                      onChange={formik.handleChange}
                      error={formik.touched.browser_settings?.viewport_width && Boolean(formik.errors.browser_settings?.viewport_width)}
                      helperText={formik.touched.browser_settings?.viewport_width && formik.errors.browser_settings?.viewport_width}
                      InputProps={{ inputProps: { min: 800, max: 1920 } }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Viewport Höhe"
                      name="browser_settings.viewport_height"
                      type="number"
                      value={formik.values.browser_settings.viewport_height}
                      onChange={formik.handleChange}
                      error={formik.touched.browser_settings?.viewport_height && Boolean(formik.errors.browser_settings?.viewport_height)}
                      helperText={formik.touched.browser_settings?.viewport_height && formik.errors.browser_settings?.viewport_height}
                      InputProps={{ inputProps: { min: 600, max: 1080 } }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Ratenbegrenzungseinstellungen */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Ratenbegrenzungseinstellungen
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Max. Anfragen pro Stunde"
                      name="rate_limiting.max_requests_per_hour"
                      type="number"
                      value={formik.values.rate_limiting.max_requests_per_hour}
                      onChange={formik.handleChange}
                      error={formik.touched.rate_limiting?.max_requests_per_hour && Boolean(formik.errors.rate_limiting?.max_requests_per_hour)}
                      helperText={formik.touched.rate_limiting?.max_requests_per_hour && formik.errors.rate_limiting?.max_requests_per_hour}
                      InputProps={{ inputProps: { min: 10, max: 1000 } }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Max. Verbindungen pro Tag"
                      name="rate_limiting.max_connections_per_day"
                      type="number"
                      value={formik.values.rate_limiting.max_connections_per_day}
                      onChange={formik.handleChange}
                      error={formik.touched.rate_limiting?.max_connections_per_day && Boolean(formik.errors.rate_limiting?.max_connections_per_day)}
                      helperText={formik.touched.rate_limiting?.max_connections_per_day && formik.errors.rate_limiting?.max_connections_per_day}
                      InputProps={{ inputProps: { min: 1, max: 100 } }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Max. Interaktionen pro Tag"
                      name="rate_limiting.max_interactions_per_day"
                      type="number"
                      value={formik.values.rate_limiting.max_interactions_per_day}
                      onChange={formik.handleChange}
                      error={formik.touched.rate_limiting?.max_interactions_per_day && Boolean(formik.errors.rate_limiting?.max_interactions_per_day)}
                      helperText={formik.touched.rate_limiting?.max_interactions_per_day && formik.errors.rate_limiting?.max_interactions_per_day}
                      InputProps={{ inputProps: { min: 10, max: 500 } }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Max. Nachrichten pro Tag"
                      name="rate_limiting.max_messages_per_day"
                      type="number"
                      value={formik.values.rate_limiting.max_messages_per_day}
                      onChange={formik.handleChange}
                      error={formik.touched.rate_limiting?.max_messages_per_day && Boolean(formik.errors.rate_limiting?.max_messages_per_day)}
                      helperText={formik.touched.rate_limiting?.max_messages_per_day && formik.errors.rate_limiting?.max_messages_per_day}
                      InputProps={{ inputProps: { min: 1, max: 50 } }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default Settings; 