import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 120000,
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/documents/upload", formData);

  return response.data;
};

export const askQuestion = async (question) => {
  const response = await api.post("/chat/", { question });

  return response.data;
};

export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }

  if (error.code === "ECONNABORTED") {
    return "The request took too long. Please try again.";
  }

  if (!error.response) {
    return "Cannot connect to the backend. Make sure the FastAPI server is running.";
  }

  return "Something went wrong. Please try again.";
};
