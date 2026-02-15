import { Link } from "react-router-dom";
import { Card, CardContent, CardActionArea, Typography, Chip, Box } from "@mui/material";
import type { SurveyResponse } from "../types/survey";

interface Props {
  survey: SurveyResponse;
}

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

export default function SurveyCard({ survey }: Props) {
  return (
    <Card>
      <CardActionArea component={Link} to={`/surveys/${survey.id}`}>
        <CardContent>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
            <Typography variant="h6" component="div">
              {survey.conferenceType} {survey.year}
            </Typography>
            <Chip
              label={survey.status}
              color={statusColor(survey.status)}
              size="small"
            />
          </Box>
          <Typography color="text.secondary">
            {survey.paperCount} papers
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
