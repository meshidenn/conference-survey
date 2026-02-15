import { useEffect, useRef } from "react";
import { Transformer } from "markmap-lib";
import { Markmap } from "markmap-view";
import { Box, Paper, Typography } from "@mui/material";
import type { MindmapNode, MindmapResponse } from "../types/survey";

interface Props {
  mindmap: MindmapResponse | null;
}

function nodeToMarkdown(node: MindmapNode, depth: number = 0): string {
  const indent = "#".repeat(depth + 1);
  const summary = node.summary ? ` - ${node.summary}` : "";
  const paperInfo = node.paperCount > 0 ? ` (${node.paperCount} papers)` : "";
  let md = `${indent} ${node.name}${paperInfo}${summary}\n`;
  for (const child of node.children) {
    md += nodeToMarkdown(child, depth + 1);
  }
  return md;
}

function mindmapToMarkdown(mindmap: MindmapResponse): string {
  let md = `# ${mindmap.conferenceType} ${mindmap.year}\n`;
  for (const root of mindmap.rootNodes) {
    md += nodeToMarkdown(root, 1);
  }
  return md;
}

export default function MindmapView({ mindmap }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const markmapRef = useRef<Markmap | null>(null);

  useEffect(() => {
    if (!svgRef.current || !mindmap || mindmap.rootNodes.length === 0) return;

    const transformer = new Transformer();
    const markdown = mindmapToMarkdown(mindmap);
    const { root } = transformer.transform(markdown);

    if (markmapRef.current) {
      markmapRef.current.setData(root);
      markmapRef.current.fit();
    } else {
      markmapRef.current = Markmap.create(svgRef.current, {}, root);
    }
  }, [mindmap]);

  if (!mindmap || mindmap.rootNodes.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: "center" }}>
        <Typography color="text.secondary">
          Mindmap will be displayed after processing completes
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, height: 500 }}>
      <Box sx={{ width: "100%", height: "100%" }}>
        <svg ref={svgRef} style={{ width: "100%", height: "100%" }} />
      </Box>
    </Paper>
  );
}
