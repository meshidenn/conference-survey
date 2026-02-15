import { Outlet, Link, useLocation } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Breadcrumbs,
} from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";

export default function Layout() {
  const location = useLocation();
  const pathParts = location.pathname.split("/").filter(Boolean);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{ color: "inherit", textDecoration: "none", flexGrow: 1 }}
          >
            Conference Survey
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 3, mb: 3, flex: 1 }}>
        {pathParts.length > 0 && (
          <Breadcrumbs sx={{ mb: 2 }}>
            <Link
              to="/"
              style={{
                display: "flex",
                alignItems: "center",
                color: "inherit",
              }}
            >
              <HomeIcon sx={{ mr: 0.5 }} fontSize="small" />
              Home
            </Link>
            {pathParts[0] === "surveys" && pathParts[1] && (
              <Link to={`/surveys/${pathParts[1]}`} style={{ color: "inherit" }}>
                Survey Detail
              </Link>
            )}
            {pathParts[2] === "tags" && (
              <Typography color="text.primary">Tags</Typography>
            )}
          </Breadcrumbs>
        )}
        <Outlet />
      </Container>
    </Box>
  );
}
