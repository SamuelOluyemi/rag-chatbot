import { useState } from "react";
import { uploadFile } from "../api";

console.log("Upload component loaded");

export default function Upload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleUpload = async () => {
    console.log("Upload clicked");
    if (!file) {
      console.log("No file selected");
      return;
    }
    console.log("Uploading file:", file);

    setStatus("Uploading...");
    try {
      await uploadFile(file);
      setStatus("Upload successful ✅");
    } catch (err) {
      setStatus("Upload failed ❌");
    }
  };

  return (
    <div className="card">
      <h2>Upload Document</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload</button>
      <p>{status}</p>
    </div>
  );
}
