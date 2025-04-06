import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  LinkedIn as LinkedInIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  School as SchoolIcon,
  Work as WorkIcon,
  Language as LanguageIcon,
  PhotoCamera as PhotoCameraIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

interface ProfileData {
  id: number;
  linkedin_id: string;
  first_name: string;
  last_name: string;
  headline: string;
  summary: string;
  profile_picture_url: string;
  cover_picture_url: string;
  email: string;
  phone: string;
  location: string;
  industry: string;
  current_position: string;
  current_company: string;
  company_website: string;
  company_size: string;
  company_industry: string;
  company_location: string;
  company_description: string;
  education: {
    id: number;
    school: string;
    degree: string;
    field_of_study: string;
    start_date: string;
    end_date: string | null;
    description: string;
  }[];
  experience: {
    id: number;
    title: string;
    company: string;
    location: string;
    start_date: string;
    end_date: string | null;
    description: string;
    current: boolean;
  }[];
  skills: {
    id: number;
    name: string;
    endorsements: number;
  }[];
  languages: {
    id: number;
    name: string;
    proficiency: string;
  }[];
  certifications: {
    id: number;
    name: string;
    issuing_organization: string;
    issue_date: string;
    expiration_date: string | null;
    credential_id: string;
    credential_url: string;
  }[];
  volunteer_experience: {
    id: number;
    organization: string;
    role: string;
    cause: string;
    start_date: string;
    end_date: string | null;
    description: string;
  }[];
  publications: {
    id: number;
    title: string;
    publisher: string;
    publication_date: string;
    description: string;
    url: string;
  }[];
  honors_awards: {
    id: number;
    title: string;
    issuer: string;
    issue_date: string;
    description: string;
  }[];
  projects: {
    id: number;
    title: string;
    description: string;
    start_date: string;
    end_date: string | null;
    url: string;
    associated_with: string;
  }[];
  recommendations: {
    id: number;
    recommender_name: string;
    recommender_title: string;
    recommender_company: string;
    recommendation_text: string;
    recommendation_date: string;
  }[];
  connections_count: number;
  profile_views: number;
  post_impressions: number;
  last_updated: string;
}

const Profile: React.FC = () => {
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editedProfile, setEditedProfile] = useState<Partial<ProfileData> | null>(null);
  const [photoDialogOpen, setPhotoDialogOpen] = useState<boolean>(false);
  const [photoType, setPhotoType] = useState<'profile' | 'cover'>('profile');
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/profile');
      if (!response.ok) {
        throw new Error('Fehler beim Laden des Profils');
      }
      const data = await response.json();
      setProfileData(data);
      setError('');
    } catch (err) {
      setError('Fehler beim Laden des Profils');
    } finally {
      setLoading(false);
    }
  };

  const handleEditToggle = () => {
    if (editMode) {
      // Abbrechen der Bearbeitung
      setEditMode(false);
      setEditedProfile(null);
    } else {
      // Bearbeitung starten
      setEditMode(true);
      setEditedProfile(profileData ? { ...profileData } : null);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    if (editedProfile) {
      setEditedProfile({
        ...editedProfile,
        [field]: value,
      });
    }
  };

  const handleSaveProfile = async () => {
    if (!editedProfile) return;

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editedProfile),
      });

      if (!response.ok) {
        throw new Error('Fehler beim Speichern des Profils');
      }

      const updatedProfile = await response.json();
      setProfileData(updatedProfile);
      setEditMode(false);
      setEditedProfile(null);
      setSuccess('Profil erfolgreich aktualisiert');
      setError('');
    } catch (err) {
      setError('Fehler beim Speichern des Profils');
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoDialogOpen = (type: 'profile' | 'cover') => {
    setPhotoType(type);
    setPhotoDialogOpen(true);
  };

  const handlePhotoDialogClose = () => {
    setPhotoDialogOpen(false);
    setPhotoFile(null);
    setPhotoPreview('');
  };

  const handlePhotoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setPhotoFile(file);
      
      // Vorschau erstellen
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target && e.target.result) {
          setPhotoPreview(e.target.result as string);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePhotoUpload = async () => {
    if (!photoFile) return;

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', photoFile);
      formData.append('type', photoType);

      const response = await fetch('http://localhost:8000/api/v1/profile/photo', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Fehler beim Hochladen des Fotos');
      }

      const updatedProfile = await response.json();
      setProfileData(updatedProfile);
      handlePhotoDialogClose();
      setSuccess('Foto erfolgreich hochgeladen');
      setError('');
    } catch (err) {
      setError('Fehler beim Hochladen des Fotos');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Gegenwärtig';
    return format(new Date(dateString), 'MMMM yyyy', { locale: de });
  };

  if (loading && !profileData) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error && !profileData) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!profileData) {
    return null;
  }

  const displayProfile = editMode ? editedProfile : profileData;

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
            LinkedIn Profil
          </Typography>
          <Button
            variant={editMode ? 'outlined' : 'contained'}
            color={editMode ? 'error' : 'primary'}
            startIcon={editMode ? <CancelIcon /> : <EditIcon />}
            onClick={handleEditToggle}
          >
            {editMode ? 'Abbrechen' : 'Bearbeiten'}
          </Button>
        </Box>

        {/* Profilbild und Cover */}
        <Box sx={{ position: 'relative', mb: 3 }}>
          <Box
            sx={{
              height: 200,
              width: '100%',
              bgcolor: 'grey.300',
              position: 'relative',
              overflow: 'hidden',
              borderRadius: 1,
            }}
          >
            {displayProfile?.cover_picture_url ? (
              <img
                src={displayProfile.cover_picture_url}
                alt="Cover"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <Typography variant="body1" color="text.secondary">
                  Kein Cover-Bild
                </Typography>
              </Box>
            )}
            {editMode && (
              <IconButton
                sx={{ position: 'absolute', bottom: 8, right: 8, bgcolor: 'rgba(255, 255, 255, 0.8)' }}
                onClick={() => handlePhotoDialogOpen('cover')}
              >
                <PhotoCameraIcon />
              </IconButton>
            )}
          </Box>
          <Box
            sx={{
              position: 'absolute',
              bottom: -60,
              left: 24,
              width: 120,
              height: 120,
              borderRadius: '50%',
              border: '4px solid white',
              overflow: 'hidden',
              bgcolor: 'grey.300',
            }}
          >
            {displayProfile?.profile_picture_url ? (
              <img
                src={displayProfile.profile_picture_url}
                alt="Profilbild"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <Typography variant="body1" color="text.secondary">
                  Kein Profilbild
                </Typography>
              </Box>
            )}
            {editMode && (
              <IconButton
                sx={{ position: 'absolute', bottom: 0, right: 0, bgcolor: 'rgba(255, 255, 255, 0.8)' }}
                onClick={() => handlePhotoDialogOpen('profile')}
              >
                <PhotoCameraIcon />
              </IconButton>
            )}
          </Box>
        </Box>

        {/* Profilinformationen */}
        <Box sx={{ mt: 8, mb: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Typography variant="h4" gutterBottom>
                {editMode ? (
                  <TextField
                    fullWidth
                    value={displayProfile?.first_name || ''}
                    onChange={(e) => handleInputChange('first_name', e.target.value)}
                    variant="standard"
                  />
                ) : (
                  `${displayProfile?.first_name} ${displayProfile?.last_name}`
                )}
              </Typography>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {editMode ? (
                  <TextField
                    fullWidth
                    value={displayProfile?.headline || ''}
                    onChange={(e) => handleInputChange('headline', e.target.value)}
                    variant="standard"
                  />
                ) : (
                  displayProfile?.headline
                )}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <BusinessIcon sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="body1">
                  {editMode ? (
                    <TextField
                      fullWidth
                      value={displayProfile?.current_company || ''}
                      onChange={(e) => handleInputChange('current_company', e.target.value)}
                      variant="standard"
                    />
                  ) : (
                    displayProfile?.current_company
                  )}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="body1">
                  {editMode ? (
                    <TextField
                      fullWidth
                      value={displayProfile?.location || ''}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      variant="standard"
                    />
                  ) : (
                    displayProfile?.location
                  )}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="body1">
                  {editMode ? (
                    <TextField
                      fullWidth
                      value={displayProfile?.email || ''}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      variant="standard"
                    />
                  ) : (
                    displayProfile?.email
                  )}
                </Typography>
              </Box>
              {displayProfile?.phone && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body1">
                    {editMode ? (
                      <TextField
                        fullWidth
                        value={displayProfile.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        variant="standard"
                      />
                    ) : (
                      displayProfile.phone
                    )}
                  </Typography>
                </Box>
              )}
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Profil-Statistiken
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <LinkedInIcon />
                      </ListItemIcon>
                      <ListItemText primary="Verbindungen" />
                      <ListItemSecondaryAction>
                        {formatNumber(profileData.connections_count)}
                      </ListItemSecondaryAction>
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <LanguageIcon />
                      </ListItemIcon>
                      <ListItemText primary="Profilaufrufe" />
                      <ListItemSecondaryAction>
                        {formatNumber(profileData.profile_views)}
                      </ListItemSecondaryAction>
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <WorkIcon />
                      </ListItemIcon>
                      <ListItemText primary="Beitragsimpressionen" />
                      <ListItemSecondaryAction>
                        {formatNumber(profileData.post_impressions)}
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                    Zuletzt aktualisiert: {format(new Date(profileData.last_updated), 'PPP', { locale: de })}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Zusammenfassung */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Zusammenfassung
          </Typography>
          {editMode ? (
            <TextField
              fullWidth
              multiline
              rows={4}
              value={displayProfile?.summary || ''}
              onChange={(e) => handleInputChange('summary', e.target.value)}
              variant="outlined"
            />
          ) : (
            <Typography variant="body1" paragraph>
              {displayProfile?.summary || 'Keine Zusammenfassung vorhanden.'}
            </Typography>
          )}
        </Box>

        {/* Aktuelle Position */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Aktuelle Position
          </Typography>
          <Card>
            <CardContent>
              <Typography variant="h6">
                {editMode ? (
                  <TextField
                    fullWidth
                    value={displayProfile?.current_position || ''}
                    onChange={(e) => handleInputChange('current_position', e.target.value)}
                    variant="standard"
                  />
                ) : (
                  displayProfile?.current_position
                )}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                {editMode ? (
                  <TextField
                    fullWidth
                    value={displayProfile?.current_company || ''}
                    onChange={(e) => handleInputChange('current_company', e.target.value)}
                    variant="standard"
                  />
                ) : (
                  displayProfile?.current_company
                )}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatDate(null)} - Gegenwärtig
              </Typography>
              {editMode ? (
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={displayProfile?.company_description || ''}
                  onChange={(e) => handleInputChange('company_description', e.target.value)}
                  variant="outlined"
                  sx={{ mt: 2 }}
                />
              ) : (
                <Typography variant="body1" sx={{ mt: 2 }}>
                  {displayProfile?.company_description || 'Keine Beschreibung vorhanden.'}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Erfahrung */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Erfahrung
            </Typography>
            {editMode && (
              <Button
                startIcon={<AddIcon />}
                variant="outlined"
                size="small"
              >
                Hinzufügen
              </Button>
            )}
          </Box>
          {profileData.experience.length > 0 ? (
            profileData.experience.map((exp) => (
              <Card key={exp.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6">
                    {exp.title}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    {exp.company}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(exp.start_date)} - {exp.current ? 'Gegenwärtig' : formatDate(exp.end_date)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {exp.location}
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    {exp.description}
                  </Typography>
                </CardContent>
              </Card>
            ))
          ) : (
            <Typography variant="body1" color="text.secondary">
              Keine Erfahrung vorhanden.
            </Typography>
          )}
        </Box>

        {/* Ausbildung */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Ausbildung
            </Typography>
            {editMode && (
              <Button
                startIcon={<AddIcon />}
                variant="outlined"
                size="small"
              >
                Hinzufügen
              </Button>
            )}
          </Box>
          {profileData.education.length > 0 ? (
            profileData.education.map((edu) => (
              <Card key={edu.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6">
                    {edu.school}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    {edu.degree}, {edu.field_of_study}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(edu.start_date)} - {edu.end_date ? formatDate(edu.end_date) : 'Gegenwärtig'}
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 1 }}>
                    {edu.description}
                  </Typography>
                </CardContent>
              </Card>
            ))
          ) : (
            <Typography variant="body1" color="text.secondary">
              Keine Ausbildung vorhanden.
            </Typography>
          )}
        </Box>

        {/* Fähigkeiten */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Fähigkeiten
            </Typography>
            {editMode && (
              <Button
                startIcon={<AddIcon />}
                variant="outlined"
                size="small"
              >
                Hinzufügen
              </Button>
            )}
          </Box>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {profileData.skills.length > 0 ? (
              profileData.skills.map((skill) => (
                <Chip
                  key={skill.id}
                  label={`${skill.name} (${skill.endorsements})`}
                  variant="outlined"
                />
              ))
            ) : (
              <Typography variant="body1" color="text.secondary">
                Keine Fähigkeiten vorhanden.
              </Typography>
            )}
          </Box>
        </Box>

        {/* Speichern-Button */}
        {editMode && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SaveIcon />}
              onClick={handleSaveProfile}
              disabled={loading}
            >
              Speichern
            </Button>
          </Box>
        )}
      </Paper>

      {/* Foto-Upload-Dialog */}
      <Dialog open={photoDialogOpen} onClose={handlePhotoDialogClose}>
        <DialogTitle>
          {photoType === 'profile' ? 'Profilbild hochladen' : 'Cover-Bild hochladen'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 2 }}>
            {photoPreview ? (
              <Box
                sx={{
                  width: photoType === 'profile' ? 200 : '100%',
                  height: photoType === 'profile' ? 200 : 150,
                  borderRadius: photoType === 'profile' ? '50%' : '4px',
                  overflow: 'hidden',
                  mb: 2,
                }}
              >
                <img
                  src={photoPreview}
                  alt="Vorschau"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </Box>
            ) : (
              <Box
                sx={{
                  width: photoType === 'profile' ? 200 : '100%',
                  height: photoType === 'profile' ? 200 : 150,
                  borderRadius: photoType === 'profile' ? '50%' : '4px',
                  bgcolor: 'grey.300',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  mb: 2,
                }}
              >
                <Typography variant="body1" color="text.secondary">
                  Keine Vorschau
                </Typography>
              </Box>
            )}
            <Button
              variant="outlined"
              component="label"
              startIcon={<PhotoCameraIcon />}
            >
              Bild auswählen
              <input
                type="file"
                hidden
                accept="image/*"
                onChange={handlePhotoChange}
              />
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handlePhotoDialogClose}>Abbrechen</Button>
          <Button
            onClick={handlePhotoUpload}
            variant="contained"
            color="primary"
            disabled={!photoFile}
          >
            Hochladen
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('de-DE').format(num);
};

export default Profile; 