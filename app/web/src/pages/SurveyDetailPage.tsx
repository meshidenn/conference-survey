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
import { getSurvey, getMindmap, startProcessing, getSurveyStatus } from "../services/api";
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

    let isMounted = true;

    // processing中は軽量なstatusエンドポイントをポーリング
    const interval = setInterval(async () => {
      if (!id || !isMounted) return;
      try {
        const status = await getSurveyStatus(id);
        if (!isMounted) return;
        // 完了またはエラー時はフル情報を取得（ステータスを先に変えない）
        if (status.status === "completed" || status.status === "failed") {
          clearInterval(interval);
          if (isMounted) await loadSurvey();
        } else {
          setSurvey((prev) => prev ? {
            ...prev,
            status: status.status,
            progressMessage: status.progressMessage,
            progressCurrent: status.progressCurrent,
            progressTotal: status.progressTotal,
            errorMessage: status.errorMessage,
          } : prev);
        }
      } catch {
        // ポーリングエラーは無視
      }
    }, 3000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [survey?.status, id]);

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
        {(survey.status === "pending" || survey.status === "failed") && (
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={handleStartProcessing}
            disabled={isProcessing}
          >
            {isProcessing
              ? "Starting..."
              : survey.status === "failed"
                ? "Retry Processing"
                : "Start Processing"}
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

      {survey.status === "failed" && !error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Processing failed. You can retry using the button above.
          {survey.errorMessage && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              {survey.errorMessage}
            </Typography>
          )}
        </Alert>
      )}

      {survey.status === "completed" && survey.errorMessage && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {survey.errorMessage}
        </Alert>
      )}

      {survey.status === "processing" && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: survey.progressTotal > 0 ? 1.5 : 0 }}>
            <CircularProgress size={24} />
            <Typography>
              {survey.progressMessage || "Processing..."}
              {survey.progressTotal > 0 && ` (${survey.progressCurrent}/${survey.progressTotal})`}
            </Typography>
          </Box>
          {survey.progressTotal > 0 && (
            <Box sx={{ width: "100%", bgcolor: "grey.200", borderRadius: 1, height: 8 }}>
              <Box
                sx={{
                  width: `${Math.round((survey.progressCurrent / survey.progressTotal) * 100)}%`,
                  bgcolor: "primary.main",
                  borderRadius: 1,
                  height: 8,
                  transition: "width 0.5s ease",
                }}
              />
            </Box>
          )}
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
