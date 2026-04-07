import Upload from "./components/Upload";
import Chat from "./components/Chat";
import "./styles.css";

export default function App() {
  return (
    <div className="container">
      <h1>AI Knowledge Assistant</h1>
      <Upload />
      <Chat />
    </div>
  );
}
