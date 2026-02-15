export type SurveyStatus = "pending" | "processing" | "completed" | "failed";

export type ConferenceType = "ACL" | "NAACL" | "EMNLP" | "EACL";

export interface CreateSurveyRequest {
  conferenceType: ConferenceType;
  year: number;
}

export interface SurveyResponse {
  id: string;
  conferenceType: ConferenceType;
  year: number;
  status: SurveyStatus;
  paperCount: number;
}

export interface PaperResponse {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  characteristics: string | null;
}

export interface TagNodeResponse {
  id: string;
  name: string;
  parentId: string | null;
  childIds: string[];
  paperIds: string[];
  paperCount: number;
  summary: string | null;
}

export interface SurveyDetailResponse {
  id: string;
  conferenceType: ConferenceType;
  year: number;
  status: SurveyStatus;
  papers: PaperResponse[];
  tagHierarchy: TagNodeResponse[];
}

export interface MindmapNode {
  id: string;
  name: string;
  summary: string | null;
  paperCount: number;
  children: MindmapNode[];
}

export interface MindmapResponse {
  surveyId: string;
  conferenceType: ConferenceType;
  year: number;
  rootNodes: MindmapNode[];
}
