import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import type { PaperResponse } from "../types/survey";

interface Props {
  papers: PaperResponse[];
}

export default function PaperList({ papers }: Props) {
  if (papers.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: "center" }}>
        <Typography color="text.secondary">No papers yet</Typography>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Title</TableCell>
            <TableCell>Authors</TableCell>
            <TableCell>Characteristics</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {papers.map((paper) => (
            <TableRow key={paper.id}>
              <TableCell>
                <Accordion elevation={0} disableGutters>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>{paper.title}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary">
                      {paper.abstract}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {paper.authors.join(", ")}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {paper.characteristics || "-"}
                </Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
