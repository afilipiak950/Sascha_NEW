import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Grid,
  Alert,
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';

interface PostEditorProps {
  initialValues?: {
    title: string;
    topic: string;
    content: string;
    tone: string;
    length: string;
    hashtags: string[];
  };
  onSubmit: (values: any) => Promise<void>;
}

const validationSchema = yup.object({
  title: yup.string().required('Titel ist erforderlich'),
  topic: yup.string().required('Thema ist erforderlich'),
  content: yup.string(),
  tone: yup.string().required('Ton ist erforderlich'),
  length: yup.string().required('Länge ist erforderlich'),
  hashtags: yup.array().of(yup.string()),
});

const PostEditor: React.FC<PostEditorProps> = ({ initialValues, onSubmit }) => {
  const [preview, setPreview] = useState<string>('');
  const [error, setError] = useState<string>('');

  const formik = useFormik({
    initialValues: initialValues || {
      title: '',
      topic: '',
      content: '',
      tone: 'professional',
      length: 'medium',
      hashtags: [],
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await onSubmit(values);
        setError('');
      } catch (err) {
        setError('Fehler beim Speichern des Posts');
      }
    },
  });

  const handleGenerateContent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/posts/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: formik.values.topic,
          tone: formik.values.tone,
          length: formik.values.length,
        }),
      });

      const data = await response.json();
      formik.setFieldValue('content', data.content);
      formik.setFieldValue('hashtags', data.hashtags);
      setPreview(data.content);
    } catch (err) {
      setError('Fehler bei der Content-Generierung');
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          LinkedIn Post erstellen
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                id="title"
                name="title"
                label="Titel"
                value={formik.values.title}
                onChange={formik.handleChange}
                error={formik.touched.title && Boolean(formik.errors.title)}
                helperText={formik.touched.title && formik.errors.title}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                id="topic"
                name="topic"
                label="Thema"
                value={formik.values.topic}
                onChange={formik.handleChange}
                error={formik.touched.topic && Boolean(formik.errors.topic)}
                helperText={formik.touched.topic && formik.errors.topic}
              />
            </Grid>

            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel id="tone-label">Ton</InputLabel>
                <Select
                  labelId="tone-label"
                  id="tone"
                  name="tone"
                  value={formik.values.tone}
                  onChange={formik.handleChange}
                  label="Ton"
                >
                  <MenuItem value="professional">Professionell</MenuItem>
                  <MenuItem value="casual">Locker</MenuItem>
                  <MenuItem value="formal">Formell</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel id="length-label">Länge</InputLabel>
                <Select
                  labelId="length-label"
                  id="length"
                  name="length"
                  value={formik.values.length}
                  onChange={formik.handleChange}
                  label="Länge"
                >
                  <MenuItem value="short">Kurz</MenuItem>
                  <MenuItem value="medium">Mittel</MenuItem>
                  <MenuItem value="long">Lang</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleGenerateContent}
                sx={{ mr: 2 }}
              >
                Content generieren
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => setPreview(formik.values.content)}
              >
                Vorschau anzeigen
              </Button>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={6}
                id="content"
                name="content"
                label="Inhalt"
                value={formik.values.content}
                onChange={formik.handleChange}
              />
            </Grid>

            {preview && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                  <Typography variant="h6" gutterBottom>
                    Vorschau
                  </Typography>
                  <Typography variant="body1">{preview}</Typography>
                </Paper>
              </Grid>
            )}

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formik.values.hashtags.map((tag, index) => (
                  <Chip
                    key={index}
                    label={tag}
                    onDelete={() => {
                      const newTags = formik.values.hashtags.filter((_, i) => i !== index);
                      formik.setFieldValue('hashtags', newTags);
                    }}
                  />
                ))}
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
                fullWidth
              >
                Als Entwurf speichern
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default PostEditor; 