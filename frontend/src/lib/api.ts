import axios from "axios";

// Axios client connected to the existing FastAPI backend
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "https://harvey-os.onrender.com",
  timeout: 10000,
});

export interface AnalyzeResponse {
  analysis: string;
}

export interface HabitsData {
  deep_work_hours: number;
  learning_hours: number;
  workout: number;
  networking_actions: number;
}

export interface HabitsResponse {
  habits: HabitsData;
  leverage_score: number;
}

export const api = {
  analyze: async (situation: string, mode: string = "offline", financial_stability: number = 5.0) => {
    const res = await apiClient.post<AnalyzeResponse>("/analyze", {
      situation,
      mode,
      financial_stability,
    });
    return res.data;
  },

  getHabits: async () => {
    const res = await apiClient.get<HabitsResponse>("/habits");
    return res.data;
  },

  getProfile: async () => {
    const res = await apiClient.get("/profile");
    return res.data;
  },

  getDecisions: async () => {
    // Backend doesn't have a /decisions endpoint yet based on planning, but let's mock or call it
    const res = await apiClient.get("/decisions").catch(() => ({ data: [] }));
    return res.data;
  },

  getOpportunities: async () => {
    // Mocking opportunities endpoint if it doesn't exist
    const res = await apiClient.get("/opportunities").catch(() => ({ data: [
      { id: "1", title: "Invest in Tech Startup", value: "$50K ROI", type: "Financial" },
      { id: "2", title: "New API Integration", value: "+20% Eff", type: "Strategic" },
      { id: "3", title: "Network with VC", value: "High Leverage", type: "Social" },
    ]}));
    return res.data;
  },

  getThreats: async () => {
    const res = await apiClient.get("/threats").catch(() => ({ data: [
      { id: "1", title: "Burnout Risk", level: "WARNING", description: "Deep work exceeded 12h" }
    ]}));
    return res.data;
  }
};
