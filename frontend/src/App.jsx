import { useEffect, useRef, useState } from "react";
import { askQuestion, getErrorMessage, uploadFile } from "./api";

const initialMessage = {
  role: "assistant",
  content:
    "Hello! I'm your AI Knowledge Assistant. Upload a PDF document, then ask me questions about its contents. I'll use your document to find relevant information and answer your questions.",
  sources: [],
};

export default function App() {
  const [messages, setMessages] = useState([initialMessage]);
  const [question, setQuestion] = useState("");
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [sending, setSending] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [chatError, setChatError] = useState("");

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    setUploadError("");
    setSelectedFile(file || null);
  };

  const handleUpload = async (event) => {
    event.preventDefault();

    if (!selectedFile || uploading) return;

    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setUploadError("Please select a PDF file.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setUploadError("The maximum file size is 10 MB.");
      return;
    }

    setUploading(true);
    setUploadError("");

    try {
      await uploadFile(selectedFile);

      setDocuments((current) => [
        ...current,
        {
          id: `${Date.now()}-${selectedFile.name}`,
          name: selectedFile.name,
        },
      ]);

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      setUploadError(getErrorMessage(error));
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || sending) return;

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    setQuestion("");
    setChatError("");
    setSending(true);

    try {
      const result = await askQuestion(trimmedQuestion);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources || [],
        },
      ]);
    } catch (error) {
      setChatError(getErrorMessage(error));
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-icon">K</span>
          <span>Knowledge AI</span>
        </a>

        <div className="connection-status">
          <span className="status-dot" />
          Local AI Assistant
        </div>
      </header>

      <main className="main-layout">
        <section className="intro">
          <div className="eyebrow">YOUR PERSONAL DOCUMENT ASSISTANT</div>
          <h1>Ask your documents anything.</h1>
          <p>
            Upload your PDFs and get useful answers grounded in the information
            they contain.
          </p>
        </section>

        <section className="workspace">
          <aside className="sidebar">
            <div className="panel-heading">
              <div>
                <span className="section-label">KNOWLEDGE BASE</span>
                <h2>Your documents</h2>
              </div>
              <span className="document-count">{documents.length}</span>
            </div>

            <form className="upload-form" onSubmit={handleUpload}>
              <label className="upload-area" htmlFor="pdf-upload">
                <span className="upload-icon">↑</span>
                <strong>Choose a PDF</strong>
                <span>Click to browse your files</span>
                <input
                  ref={fileInputRef}
                  id="pdf-upload"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                  disabled={uploading}
                />
              </label>

              {selectedFile && (
                <div className="selected-file">
                  <span className="pdf-icon">PDF</span>
                  <span className="selected-file-name">
                    {selectedFile.name}
                  </span>
                </div>
              )}

              <button
                className="upload-button"
                type="submit"
                disabled={!selectedFile || uploading}
              >
                {uploading ? "Processing document..." : "Upload document"}
              </button>

              <p className="upload-hint">PDF files only · Maximum 10 MB</p>

              {uploadError && (
                <div className="error-message">{uploadError}</div>
              )}
            </form>

            <div className="documents-section">
              <span className="section-label">UPLOADED FILES</span>

              {documents.length === 0 ? (
                <p className="empty-documents">
                  Your uploaded documents will appear here.
                </p>
              ) : (
                <ul className="document-list">
                  {documents.map((document) => (
                    <li key={document.id}>
                      <span className="pdf-icon">PDF</span>
                      <span className="document-name">{document.name}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="privacy-note">
              <span>🔒</span>
              <p>
                Powered by locally running AI models. Your documents are
                processed by your local backend.
              </p>
            </div>
          </aside>

          <section className="chat-panel">
            <div className="chat-header">
              <div className="assistant-avatar">✦</div>
              <div>
                <h2>AI Assistant</h2>
                <span>Ask questions about your documents</span>
              </div>
              <span className="online-indicator">Online</span>
            </div>

            <div className="messages-area">
              {messages.map((message, index) => (
                <div
                  className={`message-row ${message.role}`}
                  key={`${message.role}-${index}`}
                >
                  {message.role === "assistant" && (
                    <div className="message-avatar">✦</div>
                  )}

                  <div className="message-content">
                    <div className="message-bubble">{message.content}</div>

                    {message.sources?.length > 0 && (
                      <div className="sources">
                        <span className="sources-heading">SOURCES USED</span>

                        {message.sources.map((source, sourceIndex) => (
                          <div
                            className="source-item"
                            key={`${source.document_id}-${source.chunk_index}-${sourceIndex}`}
                          >
                            <span className="source-number">
                              {sourceIndex + 1}
                            </span>
                            <span>
                              Document {source.document_id}, chunk{" "}
                              {source.chunk_index}
                            </span>
                            <span className="similarity">
                              Similarity: {Number(source.similarity).toFixed(3)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {sending && (
                <div className="message-row assistant">
                  <div className="message-avatar">✦</div>
                  <div className="message-bubble typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {chatError && <div className="chat-error">{chatError}</div>}

            <form className="chat-form" onSubmit={handleSend}>
              <input
                type="text"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask something about your documents..."
                disabled={sending}
                maxLength={2000}
              />

              <button
                type="submit"
                disabled={!question.trim() || sending}
                aria-label="Send message"
              >
                {sending ? "..." : "↑"}
              </button>
            </form>

            <p className="chat-disclaimer">
              AI-generated responses may not always be accurate. Verify
              important information against your source documents.
            </p>
          </section>
        </section>
      </main>
    </div>
  );
}
