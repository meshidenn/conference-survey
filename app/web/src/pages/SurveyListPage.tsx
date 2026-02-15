import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Grid, Typography, Alert, CircularProgress, Box } from "@mui/material";
import SurveyForm from "../components/SurveyForm";
import SurveyCard from "../components/SurveyCard";
import { createSurvey, listSurveys } from "../services/api";
import type { CreateSurveyRequest, SurveyResponse } from "../types/survey";

export default function SurveyListPage() {
  const navigate = useNavigate();
  const [surveys, setSurveys] = useState<SurveyResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSurveys();
  }, []);

  const loadSurveys = async () => {
    try {
      setError(null);
      const data = await listSurveys();
      setSurveys(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load surveys");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (request: CreateSurveyRequest) => {
    setIsCreating(true);
    setError(null);
    try {
      const survey = await createSurvey(request);
      navigate(`/surveys/${survey.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create survey");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Surveys
      </Typography>

      <SurveyForm onSubmit={handleCreate} isLoading={isCreating} />

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : surveys.length === 0 ? (
        <Typography color="text.secondary" sx={{ textAlign: "center", mt: 4 }}>
          No surveys yet. Create one above.
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {surveys.map((survey) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={survey.id}>
              <SurveyCard survey={survey} />
            </Grid>
          ))}
        </Grid>
      )}
    </>
  );
}
