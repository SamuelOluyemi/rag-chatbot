import axios from "axios";

export const API = "http://127.0.0.1:5000"; // change after deploy

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${API}/upload`, formData);
};

export const askQuestion = async (question) => {
  return axios.post(`${API}/ask`, { question });
};
