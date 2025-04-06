import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip
} from '@mui/material';
import {
  PostAdd as PostIcon,
  Comment as CommentIcon,
  ThumbUp as LikeIcon,
  People as ConnectionIcon
} from '@mui/icons-material';

interface Post {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'scheduled' | 'published';
  scheduledFor?: string;
  publishedAt?: string;
}

interface Interaction {
  id: string;
  type: 'like' | 'comment' | 'connection';
  targetName: string;
  targetTitle: string;
  status: 'pending' | 'completed' | 'failed';
  createdAt: string;
}

const Dashboard: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const [postsResponse, interactionsResponse] = await Promise.all([
          fetch(`${process.env.REACT_APP_API_URL}/posts`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }),
          fetch(`${process.env.REACT_APP_API_URL}/interactions`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
        ]);

        if (!postsResponse.ok || !interactionsResponse.ok) {
          throw new Error('Fehler beim Laden der Daten');
        }

        const [postsData, interactionsData] = await Promise.all([
          postsResponse.json(),
          interactionsResponse.json()
        ]);

        setPosts(postsData);
        setInteractions(interactionsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ein Fehler ist aufgetreten');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'default';
      case 'scheduled':
        return 'info';
      case 'published':
        return 'success';
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Statistiken */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Box display="flex" alignItems="center">
              <PostIcon sx={{ mr: 1 }} />
              <Typography variant="h6">
                {posts.length} Beiträge
              </Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <LikeIcon sx={{ mr: 1 }} />
              <Typography variant="h6">
                {interactions.filter(i => i.type === 'like').length} Likes
              </Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <CommentIcon sx={{ mr: 1 }} />
              <Typography variant="h6">
                {interactions.filter(i => i.type === 'comment').length} Kommentare
              </Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <ConnectionIcon sx={{ mr: 1 }} />
              <Typography variant="h6">
                {interactions.filter(i => i.type === 'connection').length} Verbindungen
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Beiträge */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Beiträge
          </Typography>
          <Grid container spacing={2}>
            {posts.map((post) => (
              <Grid item xs={12} md={6} key={post.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {post.title}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {post.content.substring(0, 150)}...
                    </Typography>
                    <Chip
                      label={post.status}
                      color={getStatusColor(post.status) as any}
                      size="small"
                    />
                    {post.scheduledFor && (
                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                        Geplant für: {new Date(post.scheduledFor).toLocaleString()}
                      </Typography>
                    )}
                  </CardContent>
                  <CardActions>
                    <Button size="small">Bearbeiten</Button>
                    <Button size="small" color="primary">
                      Veröffentlichen
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Interaktionen */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Letzte Interaktionen
          </Typography>
          <Grid container spacing={2}>
            {interactions.slice(0, 6).map((interaction) => (
              <Grid item xs={12} md={4} key={interaction.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={1}>
                      {interaction.type === 'like' && <LikeIcon sx={{ mr: 1 }} />}
                      {interaction.type === 'comment' && <CommentIcon sx={{ mr: 1 }} />}
                      {interaction.type === 'connection' && <ConnectionIcon sx={{ mr: 1 }} />}
                      <Typography variant="subtitle1">
                        {interaction.targetName}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      {interaction.targetTitle}
                    </Typography>
                    <Chip
                      label={interaction.status}
                      color={getStatusColor(interaction.status) as any}
                      size="small"
                      sx={{ mt: 1 }}
                    />
                    <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                      {new Date(interaction.createdAt).toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 