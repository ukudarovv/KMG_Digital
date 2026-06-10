import axios from "axios";

export const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8010/api",
  headers: {
    "Content-Type": "application/json",
  },
});
