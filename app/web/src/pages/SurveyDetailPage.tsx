import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Typography,
  Alert,
  CircularProgress,
  Box,
  Button,
  Chip,
  Paper,
  Tabs,
  Tab,
} from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import BarChartIcon from "@mui/icons-material/BarChart";
import MindmapView from "../components/MindmapView";
import PaperList from "../components/PaperList";
import { getSurvey, getMindmap, startProcessing } from "../services/api";
import type { SurveyDetailResponse, MindmapResponse } from "../types/survey";

const statusColor = (status: string): "default" | "primary" | "success" | "error" => {
  switch (status) {
    case "pending":
      return "default";
    case "processing":
      return "primary";
    case "completed":
      return "success";
    case "failed":
      return "error";
    default:
      return "default";
  }
};

export default function SurveyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [survey, setSurvey] = useState<SurveyDetailResponse | null>(null);
  const [mindmap, setMindmap] = useState<MindmapResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tabIndex, setTabIndex] = useState(0);

  const loadSurvey = useCallback(async () => {
    if (!id) return;
    try {
      setError(null);
      const data = await getSurvey(id);
      setSurvey(data);

      if (data.status === "completed") {
        const mm = await getMindmap(id);
        setMindmap(mm);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load survey");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadSurvey();
  }, [loadSurvey]);

  useEffect(() => {
    if (!survey || survey.status !== "processing") return;

    const interval = setInterval(loadSurvey, 5000);
    return () => clearInterval(interval);
  }, [survey, loadSurvey]);

  const handleStartProcessing = async () => {
    if (!id) return;
    setIsProcessing(true);
    setError(null);
    try {
      await startProcessing(id);
      await loadSurvey();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start processing");
    } finally {
      setIsProcessing(false);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!survey) {
    return (
      <Alert severity="error">Survey not found</Alert>
    );
  }

  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Typography variant="h4">
          {survey.conferenceType} {survey.year}
        </Typography>
        <Chip
          label={survey.status}
          color={statusColor(survey.status)}
        />
        {survey.status === "pending" && (
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={handleStartProcessing}
            disabled={isProcessing}
          >
            {isProcessing ? "Starting..." : "Start Processing"}
          </Button>
        )}
        {survey.status === "completed" && (
          <Button
            component={Link}
            to={`/surveys/${id}/tags`}
            variant="outlined"
            startIcon={<BarChartIcon />}
          >
            Tag Stats
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {survey.status === "processing" && (
        <Paper sx={{ p: 3, mb: 3, display: "flex", alignItems: "center", gap: 2 }}>
          <CircularProgress size={24} />
          <Typography>Processing... This may take a while.</Typography>
        </Paper>
      )}

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
        <Tabs value={tabIndex} onChange={(_, v) => setTabIndex(v)}>
          <Tab label="Mindmap" />
          <Tab label={`Papers (${survey.papers.length})`} />
        </Tabs>
      </Box>

      {tabIndex === 0 && <MindmapView mindmap={mindmap} />}
      {tabIndex === 1 && <PaperList papers={survey.papers} />}
    </>
  );
}
