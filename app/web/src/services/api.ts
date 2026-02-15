import type {
  CreateSurveyRequest,
  SurveyResponse,
  SurveyDetailResponse,
  MindmapResponse,
} from "../types/survey";

const BASE_URL = "/api";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP error ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function createSurvey(
  request: CreateSurveyRequest
): Promise<SurveyResponse> {
  const response = await fetch(`${BASE_URL}/surveys`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return handleResponse<SurveyResponse>(response);
}

export async function listSurveys(): Promise<SurveyResponse[]> {
  const response = await fetch(`${BASE_URL}/surveys`);
  return handleResponse<SurveyResponse[]>(response);
}

export async function getSurvey(surveyId: string): Promise<SurveyDetailResponse> {
  const response = await fetch(`${BASE_URL}/surveys/${surveyId}`);
  return handleResponse<SurveyDetailResponse>(response);
}

export async function startProcessing(surveyId: string): Promise<SurveyResponse> {
  const response = await fetch(`${BASE_URL}/surveys/${surveyId}/process`, {
    method: "POST",
  });
  return handleResponse<SurveyResponse>(response);
}

export async function getMindmap(surveyId: string): Promise<MindmapResponse> {
  const response = await fetch(`${BASE_URL}/surveys/${surveyId}/mindmap`);
  return handleResponse<MindmapResponse>(response);
}
