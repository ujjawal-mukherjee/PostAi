import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [prompt, setPrompt] = useState("");
    const [response, setResponse] = useState("");
    const [history, setHistory] = useState([]);
    const [activeIndex, setActiveIndex] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!prompt.trim()) return;

        try {
            const res = await axios.post("http://localhost:8000/generate", { prompt });
            const newEntry = { prompt, response: res.data.response };
            setResponse(res.data.response);
            setHistory(prev => [...prev, newEntry]);
            setActiveIndex(history.length);
            setPrompt("");
        } catch (error) {
            console.error("Error generating post:", error);
        }
    };

    const formatResponse = (text) => {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    };

    return (
        <div className="layout">
            {/* Sidebar */}
            <div className="sidebar">
                <h2>🕘 History</h2>
                {history.map((item, index) => (
                    <div
                        key={index}
                        className={`sidebar-item ${index === activeIndex ? 'active' : ''}`}
                        onClick={() => {
                            setResponse(item.response);
                            setActiveIndex(index);
                        }}
                    >
                        {item.prompt.length > 30 ? item.prompt.slice(0, 30) + '...' : item.prompt}
                    </div>
                ))}
            </div>

            {/* Main Area */}
            <div className="main-content">
                <h1>Post Generator</h1>
                <form onSubmit={handleSubmit} className="form">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Enter your topic..."
                    />
                    <button type="submit">Generate Post</button>
                </form>

                {response && (
                    <div className="response-box">
                        <h3>✨ Generated Post</h3>
                        <div dangerouslySetInnerHTML={{ __html: formatResponse(response) }} />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
