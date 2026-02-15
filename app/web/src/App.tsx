import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import Layout from "./components/Layout";
import SurveyListPage from "./pages/SurveyListPage";
import SurveyDetailPage from "./pages/SurveyDetailPage";
import TagStatsPage from "./pages/TagStatsPage";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<SurveyListPage />} />
            <Route path="surveys/:id" element={<SurveyDetailPage />} />
            <Route path="surveys/:id/tags" element={<TagStatsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
