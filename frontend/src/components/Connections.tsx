import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Alert,
  CircularProgress,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Send as SendIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface TargetContact {
  id: number;
  name: string;
  title: string;
  company: string;
  location: string;
  industry: string;
  connection_degree: string;
  profile_url: string;
  status: 'pending' | 'connected' | 'rejected' | 'ignored';
  notes: string;
  last_contacted: string | null;
  tags: string[];
}

interface SearchFilters {
  keywords: string;
  industry: string;
  location: string;
  connection_degree: string;
  company_size: string;
  seniority: string;
}

const Connections: React.FC = () => {
  const [contacts, setContacts] = useState<TargetContact[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [searchDialogOpen, setSearchDialogOpen] = useState<boolean>(false);
  const [editDialogOpen, setEditDialogOpen] = useState<boolean>(false);
  const [selectedContact, setSelectedContact] = useState<TargetContact | null>(null);
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    keywords: '',
    industry: '',
    location: '',
    connection_degree: '',
    company_size: '',
    seniority: '',
  });
  const [newTag, setNewTag] = useState<string>('');

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/target-contacts');
      if (!response.ok) {
        throw new Error('Fehler beim Laden der Kontakte');
      }
      const data = await response.json();
      setContacts(data);
      setError('');
    } catch (err) {
      setError('Fehler beim Laden der Kontakte');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams();
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const response = await fetch(`http://localhost:8000/api/v1/target-contacts/search?${queryParams}`);
      if (!response.ok) {
        throw new Error('Fehler bei der Kontaktsuche');
      }
      const data = await response.json();
      setContacts(data);
      setSearchDialogOpen(false);
      setError('');
    } catch (err) {
      setError('Fehler bei der Kontaktsuche');
    } finally {
      setLoading(false);
    }
  };

  const handleSendConnectionRequest = async (contactId: number) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/target-contacts/${contactId}/connect`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Fehler beim Senden der Verbindungsanfrage');
      }

      const updatedContact = await response.json();
      setContacts(contacts.map(contact => 
        contact.id === contactId ? updatedContact : contact
      ));
      setSuccess('Verbindungsanfrage erfolgreich gesendet');
      setError('');
    } catch (err) {
      setError('Fehler beim Senden der Verbindungsanfrage');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateContact = async (contact: TargetContact) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/target-contacts/${contact.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(contact),
      });

      if (!response.ok) {
        throw new Error('Fehler beim Aktualisieren des Kontakts');
      }

      const updatedContact = await response.json();
      setContacts(contacts.map(c => c.id === contact.id ? updatedContact : c));
      setEditDialogOpen(false);
      setSelectedContact(null);
      setSuccess('Kontakt erfolgreich aktualisiert');
      setError('');
    } catch (err) {
      setError('Fehler beim Aktualisieren des Kontakts');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteContact = async (contactId: number) => {
    if (!window.confirm('Möchten Sie diesen Kontakt wirklich löschen?')) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/target-contacts/${contactId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Fehler beim Löschen des Kontakts');
      }

      setContacts(contacts.filter(contact => contact.id !== contactId));
      setSuccess('Kontakt erfolgreich gelöscht');
      setError('');
    } catch (err) {
      setError('Fehler beim Löschen des Kontakts');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTag = (contactId: number) => {
    if (!newTag.trim()) return;

    const contact = contacts.find(c => c.id === contactId);
    if (!contact) return;

    if (!contact.tags.includes(newTag)) {
      const updatedContact = {
        ...contact,
        tags: [...contact.tags, newTag],
      };
      handleUpdateContact(updatedContact);
    }
    setNewTag('');
  };

  const handleRemoveTag = (contactId: number, tag: string) => {
    const contact = contacts.find(c => c.id === contactId);
    if (!contact) return;

    const updatedContact = {
      ...contact,
      tags: contact.tags.filter(t => t !== tag),
    };
    handleUpdateContact(updatedContact);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'connected':
        return 'success';
      case 'rejected':
        return 'error';
      case 'ignored':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Ausstehend';
      case 'connected':
        return 'Verbunden';
      case 'rejected':
        return 'Abgelehnt';
      case 'ignored':
        return 'Ignoriert';
      default:
        return status;
    }
  };

  const handleOpenEditDialog = (contact: TargetContact) => {
    setSelectedContact(contact);
    setEditDialogOpen(true);
  };

  const handleCloseEditDialog = () => {
    setSelectedContact(null);
    setEditDialogOpen(false);
  };

  const handleInputChange = (field: string, value: any) => {
    if (selectedContact) {
      setSelectedContact({
        ...selectedContact,
        [field]: value,
      });
    }
  };

  if (loading && contacts.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
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
            LinkedIn Verbindungen
          </Typography>
          <Box>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchContacts}
              sx={{ mr: 2 }}
            >
              Aktualisieren
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SearchIcon />}
              onClick={() => setSearchDialogOpen(true)}
            >
              Kontakte suchen
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {contacts.map((contact) => (
            <Grid item xs={12} md={6} lg={4} key={contact.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
                      {contact.name}
                    </Typography>
                    <Chip
                      label={getStatusText(contact.status)}
                      color={getStatusColor(contact.status) as any}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {contact.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {contact.company}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {contact.location}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {contact.industry}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Verbindungsgrad: {contact.connection_degree}
                  </Typography>
                  {contact.last_contacted && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Zuletzt kontaktiert: {new Date(contact.last_contacted).toLocaleDateString()}
                    </Typography>
                  )}
                  {contact.notes && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Notizen: {contact.notes}
                      </Typography>
                    </Box>
                  )}
                  {contact.tags.length > 0 && (
                    <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {contact.tags.map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          size="small"
                          onDelete={() => handleRemoveTag(contact.id, tag)}
                        />
                      ))}
                    </Box>
                  )}
                  <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
                    <TextField
                      size="small"
                      placeholder="Tag hinzufügen"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleAddTag(contact.id);
                        }
                      }}
                      sx={{ mr: 1, flexGrow: 1 }}
                    />
                    <IconButton
                      size="small"
                      onClick={() => handleAddTag(contact.id)}
                      disabled={!newTag.trim()}
                    >
                      <AddIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<SendIcon />}
                    onClick={() => handleSendConnectionRequest(contact.id)}
                    disabled={contact.status !== 'pending'}
                  >
                    Verbindungsanfrage senden
                  </Button>
                  <Button
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => handleOpenEditDialog(contact)}
                  >
                    Bearbeiten
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={() => handleDeleteContact(contact.id)}
                  >
                    Löschen
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Suchdialog */}
      <Dialog open={searchDialogOpen} onClose={() => setSearchDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Kontakte suchen</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Schlüsselwörter"
                value={searchFilters.keywords}
                onChange={(e) => setSearchFilters({ ...searchFilters, keywords: e.target.value })}
                placeholder="z.B. Software Engineer, Berlin, Startup"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Industrie</InputLabel>
                <Select
                  value={searchFilters.industry}
                  onChange={(e) => setSearchFilters({ ...searchFilters, industry: e.target.value })}
                  label="Industrie"
                >
                  <MenuItem value="">Alle</MenuItem>
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
                <InputLabel>Standort</InputLabel>
                <Select
                  value={searchFilters.location}
                  onChange={(e) => setSearchFilters({ ...searchFilters, location: e.target.value })}
                  label="Standort"
                >
                  <MenuItem value="">Alle</MenuItem>
                  <MenuItem value="germany">Deutschland</MenuItem>
                  <MenuItem value="berlin">Berlin</MenuItem>
                  <MenuItem value="munich">München</MenuItem>
                  <MenuItem value="hamburg">Hamburg</MenuItem>
                  <MenuItem value="frankfurt">Frankfurt</MenuItem>
                  <MenuItem value="cologne">Köln</MenuItem>
                  <MenuItem value="austria">Österreich</MenuItem>
                  <MenuItem value="switzerland">Schweiz</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Verbindungsgrad</InputLabel>
                <Select
                  value={searchFilters.connection_degree}
                  onChange={(e) => setSearchFilters({ ...searchFilters, connection_degree: e.target.value })}
                  label="Verbindungsgrad"
                >
                  <MenuItem value="">Alle</MenuItem>
                  <MenuItem value="1">1. Verbindung</MenuItem>
                  <MenuItem value="2">2. Verbindung</MenuItem>
                  <MenuItem value="3">3. Verbindung</MenuItem>
                  <MenuItem value="out_of_network">Außerhalb des Netzwerks</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Unternehmensgröße</InputLabel>
                <Select
                  value={searchFilters.company_size}
                  onChange={(e) => setSearchFilters({ ...searchFilters, company_size: e.target.value })}
                  label="Unternehmensgröße"
                >
                  <MenuItem value="">Alle</MenuItem>
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
                <InputLabel>Seniorität</InputLabel>
                <Select
                  value={searchFilters.seniority}
                  onChange={(e) => setSearchFilters({ ...searchFilters, seniority: e.target.value })}
                  label="Seniorität"
                >
                  <MenuItem value="">Alle</MenuItem>
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
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSearchDialogOpen(false)}>Abbrechen</Button>
          <Button onClick={handleSearch} variant="contained" color="primary">
            Suchen
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bearbeitungsdialog */}
      <Dialog open={editDialogOpen} onClose={handleCloseEditDialog} maxWidth="md" fullWidth>
        <DialogTitle>Kontakt bearbeiten</DialogTitle>
        <DialogContent>
          {selectedContact && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Name"
                  value={selectedContact.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Position"
                  value={selectedContact.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Unternehmen"
                  value={selectedContact.company}
                  onChange={(e) => handleInputChange('company', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Standort"
                  value={selectedContact.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Industrie"
                  value={selectedContact.industry}
                  onChange={(e) => handleInputChange('industry', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Verbindungsgrad</InputLabel>
                  <Select
                    value={selectedContact.connection_degree}
                    onChange={(e) => handleInputChange('connection_degree', e.target.value)}
                    label="Verbindungsgrad"
                  >
                    <MenuItem value="1">1. Verbindung</MenuItem>
                    <MenuItem value="2">2. Verbindung</MenuItem>
                    <MenuItem value="3">3. Verbindung</MenuItem>
                    <MenuItem value="out_of_network">Außerhalb des Netzwerks</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Profil-URL"
                  value={selectedContact.profile_url}
                  onChange={(e) => handleInputChange('profile_url', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={selectedContact.status}
                    onChange={(e) => handleInputChange('status', e.target.value)}
                    label="Status"
                  >
                    <MenuItem value="pending">Ausstehend</MenuItem>
                    <MenuItem value="connected">Verbunden</MenuItem>
                    <MenuItem value="rejected">Abgelehnt</MenuItem>
                    <MenuItem value="ignored">Ignoriert</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notizen"
                  value={selectedContact.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  multiline
                  rows={3}
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Tags
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {selectedContact.tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      onDelete={() => handleRemoveTag(selectedContact.id, tag)}
                    />
                  ))}
                </Box>
                <Box sx={{ display: 'flex' }}>
                  <TextField
                    fullWidth
                    label="Neuer Tag"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleAddTag(selectedContact.id);
                      }
                    }}
                  />
                  <Button
                    variant="contained"
                    onClick={() => handleAddTag(selectedContact.id)}
                    sx={{ ml: 1 }}
                    disabled={!newTag.trim()}
                  >
                    <AddIcon />
                  </Button>
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>Abbrechen</Button>
          <Button
            onClick={() => selectedContact && handleUpdateContact(selectedContact)}
            variant="contained"
            color="primary"
          >
            Speichern
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Connections; 