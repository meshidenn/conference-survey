import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Typography,
  Alert,
  CircularProgress,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
} from "@mui/material";
import { getSurvey } from "../services/api";
import type { SurveyDetailResponse, TagNodeResponse } from "../types/survey";

export default function TagStatsPage() {
  const { id } = useParams<{ id: string }>();
  const [survey, setSurvey] = useState<SurveyDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSurvey = async () => {
      if (!id) return;
      try {
        setError(null);
        const data = await getSurvey(id);
        setSurvey(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load survey");
      } finally {
        setIsLoading(false);
      }
    };
    loadSurvey();
  }, [id]);

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!survey) {
    return <Alert severity="error">Survey not found</Alert>;
  }

  const tags = survey.tagHierarchy;
  const maxCount = Math.max(...tags.map((t) => t.paperCount), 1);

  const sortedTags = [...tags].sort((a, b) => b.paperCount - a.paperCount);

  const getTagLevel = (tag: TagNodeResponse): number => {
    if (!tag.parentId) return 0;
    const parent = tags.find((t) => t.id === tag.parentId);
    return parent ? getTagLevel(parent) + 1 : 0;
  };

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Tag Statistics: {survey.conferenceType} {survey.year}
      </Typography>

      {tags.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: "center" }}>
          <Typography color="text.secondary">
            No tags yet. Processing must be completed first.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Tag</TableCell>
                <TableCell>Level</TableCell>
                <TableCell align="right">Papers</TableCell>
                <TableCell sx={{ width: "40%" }}>Distribution</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedTags.map((tag) => (
                <TableRow key={tag.id}>
                  <TableCell>
                    <Typography fontWeight={tag.parentId ? "normal" : "bold"}>
                      {tag.name}
                    </Typography>
                    {tag.summary && (
                      <Typography variant="body2" color="text.secondary">
                        {tag.summary}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>{getTagLevel(tag)}</TableCell>
                  <TableCell align="right">{tag.paperCount}</TableCell>
                  <TableCell>
                    <LinearProgress
                      variant="determinate"
                      value={(tag.paperCount / maxCount) * 100}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </>
  );
}
