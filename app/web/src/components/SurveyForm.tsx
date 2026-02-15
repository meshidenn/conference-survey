import { useState } from "react";
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Paper,
  Typography,
} from "@mui/material";
import type { ConferenceType, CreateSurveyRequest } from "../types/survey";

interface Props {
  onSubmit: (request: CreateSurveyRequest) => Promise<void>;
  isLoading: boolean;
}

const CONFERENCE_TYPES: ConferenceType[] = ["ACL", "NAACL", "EMNLP", "EACL"];

export default function SurveyForm({ onSubmit, isLoading }: Props) {
  const [conferenceType, setConferenceType] = useState<ConferenceType>("ACL");
  const [year, setYear] = useState<number>(new Date().getFullYear());

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({ conferenceType, year });
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Create New Survey
      </Typography>
      <Box component="form" onSubmit={handleSubmit} sx={{ display: "flex", gap: 2, alignItems: "flex-end", flexWrap: "wrap" }}>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel id="conference-label">Conference</InputLabel>
          <Select
            labelId="conference-label"
            value={conferenceType}
            label="Conference"
            onChange={(e) => setConferenceType(e.target.value as ConferenceType)}
          >
            {CONFERENCE_TYPES.map((type) => (
              <MenuItem key={type} value={type}>
                {type}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          label="Year"
          type="number"
          value={year}
          onChange={(e) => setYear(parseInt(e.target.value, 10))}
          inputProps={{ min: 1900, max: 2100 }}
          sx={{ width: 120 }}
        />
        <Button
          type="submit"
          variant="contained"
          disabled={isLoading}
          sx={{ height: 56 }}
        >
          {isLoading ? "Creating..." : "Create"}
        </Button>
      </Box>
    </Paper>
  );
}
