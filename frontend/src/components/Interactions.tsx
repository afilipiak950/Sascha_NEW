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
  Tabs,
  Tab,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  ThumbUp as LikeIcon,
  Comment as CommentIcon,
  PersonAdd as FollowIcon,
  Send as SendIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  AutoFixHigh as AIIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

interface Interaction {
  id: number;
  type: 'like' | 'comment' | 'follow' | 'connection_request' | 'message' | 'share';
  target_url: string;
  target_name: string;
  target_title: string;
  content: string;
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
  scheduled_for: string | null;
  error_message: string | null;
  notes: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const Interactions: React.FC = () => {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [tabValue, setTabValue] = useState<number>(0);
  const [commentDialogOpen, setCommentDialogOpen] = useState<boolean>(false);
  const [selectedInteraction, setSelectedInteraction] = useState<Interaction | null>(null);
  const [commentContent, setCommentContent] = useState<string>('');
  const [generatingComment, setGeneratingComment] = useState<boolean>(false);

  useEffect(() => {
    fetchInteractions();
  }, []);

  const fetchInteractions = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/interactions');
      if (!response.ok) {
        throw new Error('Fehler beim Laden der Interaktionen');
      }
      const data = await response.json();
      setInteractions(data);
      setError('');
    } catch (err) {
      setError('Fehler beim Laden der Interaktionen');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleDeleteInteraction = async (interactionId: number) => {
    if (!window.confirm('Möchten Sie diese Interaktion wirklich löschen?')) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/interactions/${interactionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Fehler beim Löschen der Interaktion');
      }

      setInteractions(interactions.filter(interaction => interaction.id !== interactionId));
      setSuccess('Interaktion erfolgreich gelöscht');
      setError('');
    } catch (err) {
      setError('Fehler beim Löschen der Interaktion');
    } finally {
      setLoading(false);
    }
  };

  const handleRetryInteraction = async (interactionId: number) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/interactions/${interactionId}/retry`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Fehler beim Wiederholen der Interaktion');
      }

      const updatedInteraction = await response.json();
      setInteractions(interactions.map(interaction => 
        interaction.id === interactionId ? updatedInteraction : interaction
      ));
      setSuccess('Interaktion wird wiederholt');
      setError('');
    } catch (err) {
      setError('Fehler beim Wiederholen der Interaktion');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCommentDialog = (interaction: Interaction) => {
    setSelectedInteraction(interaction);
    setCommentContent(interaction.content || '');
    setCommentDialogOpen(true);
  };

  const handleCloseCommentDialog = () => {
    setSelectedInteraction(null);
    setCommentContent('');
    setCommentDialogOpen(false);
  };

  const handleGenerateComment = async () => {
    if (!selectedInteraction) return;

    try {
      setGeneratingComment(true);
      const response = await fetch('http://localhost:8000/api/v1/interactions/generate-comment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target_name: selectedInteraction.target_name,
          target_title: selectedInteraction.target_title,
          target_url: selectedInteraction.target_url,
        }),
      });

      if (!response.ok) {
        throw new Error('Fehler bei der Generierung des Kommentars');
      }

      const data = await response.json();
      setCommentContent(data.content);
      setError('');
    } catch (err) {
      setError('Fehler bei der Generierung des Kommentars');
    } finally {
      setGeneratingComment(false);
    }
  };

  const handleSubmitComment = async () => {
    if (!selectedInteraction || !commentContent.trim()) return;

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/interactions/${selectedInteraction.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...selectedInteraction,
          content: commentContent,
        }),
      });

      if (!response.ok) {
        throw new Error('Fehler beim Speichern des Kommentars');
      }

      const updatedInteraction = await response.json();
      setInteractions(interactions.map(interaction => 
        interaction.id === selectedInteraction.id ? updatedInteraction : interaction
      ));
      setCommentDialogOpen(false);
      setSuccess('Kommentar erfolgreich gespeichert');
      setError('');
    } catch (err) {
      setError('Fehler beim Speichern des Kommentars');
    } finally {
      setLoading(false);
    }
  };

  const getInteractionIcon = (type: string) => {
    switch (type) {
      case 'like':
        return <LikeIcon />;
      case 'comment':
        return <CommentIcon />;
      case 'follow':
        return <FollowIcon />;
      case 'connection_request':
        return <PersonAddIcon />;
      case 'message':
        return <SendIcon />;
      case 'share':
        return <ShareIcon />;
      default:
        return null;
    }
  };

  const getInteractionTypeText = (type: string) => {
    switch (type) {
      case 'like':
        return 'Like';
      case 'comment':
        return 'Kommentar';
      case 'follow':
        return 'Folgen';
      case 'connection_request':
        return 'Verbindungsanfrage';
      case 'message':
        return 'Nachricht';
      case 'share':
        return 'Teilen';
      default:
        return type;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Ausstehend';
      case 'completed':
        return 'Abgeschlossen';
      case 'failed':
        return 'Fehlgeschlagen';
      default:
        return status;
    }
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'dd.MM.yyyy HH:mm', { locale: de });
  };

  const filteredInteractions = interactions.filter(interaction => {
    if (tabValue === 0) return true;
    return interaction.type === ['all', 'like', 'comment', 'follow', 'connection_request', 'message', 'share'][tabValue];
  });

  if (loading && interactions.length === 0) {
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
            LinkedIn Interaktionen
          </Typography>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchInteractions}
          >
            Aktualisieren
          </Button>
        </Box>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="interaction tabs">
            <Tab label="Alle" />
            <Tab label="Likes" />
            <Tab label="Kommentare" />
            <Tab label="Folgen" />
            <Tab label="Verbindungen" />
            <Tab label="Nachrichten" />
            <Tab label="Teilen" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={tabValue}>
          <Grid container spacing={3}>
            {filteredInteractions.map((interaction) => (
              <Grid item xs={12} md={6} key={interaction.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ mr: 1, color: 'primary.main' }}>
                          {getInteractionIcon(interaction.type)}
                        </Box>
                        <Typography variant="h6" component="div">
                          {getInteractionTypeText(interaction.type)}
                        </Typography>
                      </Box>
                      <Chip
                        label={getStatusText(interaction.status)}
                        color={getStatusColor(interaction.status) as any}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Ziel: {interaction.target_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Position: {interaction.target_title}
                    </Typography>
                    {interaction.content && (
                      <Box sx={{ mt: 1, mb: 1 }}>
                        <Typography variant="body2">
                          {interaction.content}
                        </Typography>
                      </Box>
                    )}
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Erstellt: {formatDate(interaction.created_at)}
                    </Typography>
                    {interaction.scheduled_for && (
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Geplant für: {formatDate(interaction.scheduled_for)}
                      </Typography>
                    )}
                    {interaction.error_message && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="error">
                          Fehler: {interaction.error_message}
                        </Typography>
                      </Box>
                    )}
                    {interaction.notes && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Notizen: {interaction.notes}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                  <CardActions>
                    {interaction.type === 'comment' && (
                      <Button
                        size="small"
                        startIcon={<CommentIcon />}
                        onClick={() => handleOpenCommentDialog(interaction)}
                      >
                        Kommentar bearbeiten
                      </Button>
                    )}
                    {interaction.status === 'failed' && (
                      <Button
                        size="small"
                        color="primary"
                        onClick={() => handleRetryInteraction(interaction.id)}
                      >
                        Wiederholen
                      </Button>
                    )}
                    <Button
                      size="small"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => handleDeleteInteraction(interaction.id)}
                    >
                      Löschen
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
      </Paper>

      {/* Kommentar-Dialog */}
      <Dialog open={commentDialogOpen} onClose={handleCloseCommentDialog} maxWidth="md" fullWidth>
        <DialogTitle>Kommentar bearbeiten</DialogTitle>
        <DialogContent>
          {selectedInteraction && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Ziel: {selectedInteraction.target_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Position: {selectedInteraction.target_title}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Kommentar"
                  value={commentContent}
                  onChange={(e) => setCommentContent(e.target.value)}
                  multiline
                  rows={4}
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  startIcon={<AIIcon />}
                  onClick={handleGenerateComment}
                  disabled={generatingComment}
                >
                  {generatingComment ? 'Generiere Kommentar...' : 'KI-Kommentar generieren'}
                </Button>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCommentDialog}>Abbrechen</Button>
          <Button
            onClick={handleSubmitComment}
            variant="contained"
            color="primary"
            disabled={!commentContent.trim()}
          >
            Speichern
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Interactions; 