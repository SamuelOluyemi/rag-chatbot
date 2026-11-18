// // Before deployment
// import axios from "axios";

// export const API = "http://127.0.0.1:5000"; // change after deploy

// export const uploadFile = async (file) => {
//   const formData = new FormData();
//   formData.append("file", file);

//   return axios.post(`${API}/upload`, formData);
// };

// export const askQuestion = async (question) => {
//   return axios.post(`${API}/ask`, { question });
// };

// After deployment
import axios from "axios";

export const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

const axiosInstance = axios.create({
  baseURL: API,
  headers: {
    "Content-Type": "application/json",
  },
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await axiosInstance.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  } catch (error) {
    console.error("Upload error:", error);
    throw error;
  }
};

export const askQuestion = async (question) => {
  try {
    const res = await axiosInstance.post("/ask", { question });
    return res.data;
  } catch (error) {
    console.error("Ask error:", error);
    throw error;
  }
};