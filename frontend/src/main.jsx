import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Send, Plus, MessageSquare, Code2, Calculator, Settings, PanelLeftClose, Copy, Check, Sparkles, Menu, Play, AlertTriangle } from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || '/api';
const starter = [{ role: 'assistant', content: 'Hello! I’m HARVIX, your AI coding and mathematics assistant.\n\nI can help you build, debug, explain, and solve — with clear, reliable answers.' }];

function extractCode(text) {
  const match = text.match(/```([\\w+#-]*)\\n([\\s\\S]*?)```/);
  return match ? { language: match[1] || 'python', code: match[2].trim() } : null;
}

function renderMarkdown(text) {
  const parts = text.split(/```([\\w+#-]*)\\n([\\s\\S]*?)```/g);
  const nodes = [];
  for (let i = 0; i < parts.length; i += 3) {
    const prose = parts[i];
    if (prose) {
      prose.split('\n').forEach((line, index) => {
        if (line.startsWith('### ')) nodes.push(<h3 key={`h-${i}-${index}`}>{line.slice(4)}</h3>);
        else if (line.startsWith('- ')) nodes.push(<div className="bullet" key={`b-${i}-${index}`}>• {line.slice(2)}</div>);
        else nodes.push(<React.Fragment key={`p-${i}-${index}`}>{line}{index < prose.split('\n').length - 1 && <br />}</React.Fragment>);
      });
    }
    if (i + 1 < parts.length) {
      const language = parts[i + 1] || 'python';
      const code = parts[i + 2];
      nodes.push(<pre className="code-block" key={`code-${i}`}><code>{code}</code></pre>);
    }
  }
  return nodes;
}

function App() {
  const [messages, setMessages] = useState(starter);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState('auto');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [sidebar, setSidebar] = useState(true);
  const [runResult, setRunResult] = useState(null);

  const lastAssistant = useMemo(() => [...messages].reverse().find((m) => m.role === 'assistant'), [messages]);

  const send = async (text = input) => {
    const prompt = text.trim();
    if (!prompt || loading) return;
    setInput('');
    setRunResult(null);
    const history = messages.map(({ role, content }) => ({ role, content }));
    setMessages((current) => [...current, { role: 'user', content: prompt }]);
    setLoading(true);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: prompt, mode, history }),
        signal: controller.signal,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
      const content = data.response ?? data.reply ?? data.output;
      if (typeof content !== 'string' || !content.trim()) throw new Error('The backend returned an empty response.');
      setMessages((current) => [...current, { role: 'assistant', content, mode: data.mode, elapsed: data.elapsed_ms, sources: data.sources }]);
    } catch (error) {
      const reason = error.name === 'AbortError' ? 'The request timed out after 30 seconds.' : error.message;
      setMessages((current) => [...current, { role: 'assistant', error: true, content: `Unable to generate the response.\n\nReason: ${reason}\n\nPlease try again.` }]);
    } finally {
      clearTimeout(timeout);
      setLoading(false);
    }
  };

  const runCode = async (code) => {
    setRunResult({ loading: true });
    try {
      const response = await fetch(`${API}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'python', code, stdin: '' }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `Execution failed (${response.status})`);
      setRunResult(data);
    } catch (error) {
      setRunResult({ success: false, output: '', error: error.message, exit_code: 1 });
    }
  };

  const copyCode = (code) => {
    navigator.clipboard?.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return <div className="app">
    <aside className={sidebar ? 'sidebar' : 'sidebar closed'}>
      <div className="brand"><div className="brandmark">H</div><div><b>HARVIX</b><span>AI WORKSPACE</span></div></div>
      <button className="newchat" onClick={() => { setMessages(starter); setRunResult(null); }}><Plus size={18} /> New conversation</button>
      <div className="section"><small>WORKSPACE</small>
        <div className="nav active"><MessageSquare size={17} /> Chat <kbd>⌘ 1</kbd></div>
        <div className="nav" onClick={() => setMode('coding')}><Code2 size={17} /> Coding mode</div>
        <div className="nav" onClick={() => setMode('math')}><Calculator size={17} /> Math solver</div>
      </div>
      <div className="section history"><small>RECENT CHATS</small><div className="historyitem">Binary search program</div><div className="historyitem">Quadratic equation solver</div><div className="historyitem">API execution test</div></div>
      <div className="user"><div className="avatar">CS</div><div><b>Castrosunil</b><span>Free workspace</span></div><Settings size={17} /></div>
    </aside>
    <main>
      <header><button className="iconbtn" onClick={() => setSidebar(!sidebar)}><Menu size={20} /></button><div><h1>AI workspace</h1><p>Ask HARVIX anything</p></div><div className="status"><i /> System operational <button className="iconbtn"><PanelLeftClose size={18} /></button></div></header>
      <div className="content"><div className="chat">
        <div className="welcome"><div className="spark"><Sparkles size={22} /></div><div><h2>How can I help you today?</h2><p>Explore ideas, solve problems, and ship better code.</p></div></div>
        {messages.map((message, index) => <div className={`message ${message.role}`} key={`${index}-${message.content.slice(0, 12)}`}><div className="msgavatar">{message.role === 'assistant' ? 'H' : 'CS'}</div><div className={`bubble ${message.error ? 'error-bubble' : ''}`}>
          <div className="meta">{message.role === 'assistant' ? 'HARVIX' : 'You'} {message.mode && <span className="tag">{message.mode}</span>}</div>
          <div className="text">{message.role === 'assistant' ? renderMarkdown(message.content) : message.content}</div>
          {message.role === 'assistant' && !message.error && index > 0 && <div className="response-actions"><button className="copy" onClick={() => copyCode(extractCode(message.content)?.code || message.content)}>{copied ? <Check size={14} /> : <Copy size={14} />} {copied ? 'Copied' : 'Copy'}</button>{extractCode(message.content)?.language === 'python' && <button className="copy" onClick={() => runCode(extractCode(message.content).code)}><Play size={14} /> Run Code</button>}</div>}
        </div></div>)}
        {loading && <div className="message assistant"><div className="msgavatar">H</div><div className="bubble"><div className="meta">HARVIX <span className="tag">thinking</span></div><div className="typing"><i /><i /><i /></div></div></div>}
        {runResult && !runResult.loading && <div className={`execution-result ${runResult.success ? 'success' : 'failure'}`}><div className="execution-title"><Play size={14} /> {runResult.success ? 'OUTPUT' : 'ERROR'}</div><pre>{runResult.success ? (runResult.output || '(no stdout)') : runResult.error}</pre></div>}
        <div className="suggestions"><button onClick={() => send('Write a Python program for binary search.')}> <Code2 size={16} /> Binary search</button><button onClick={() => send('Create a Python program to find the largest number in an array.')}> <Code2 size={16} /> Largest in array</button><button onClick={() => send('Solve 2*x^2 - 5*x + 3 = 0 step by step')}> <Calculator size={16} /> Solve math</button></div>
      </div></div>
      <div className="composer"><div className="modebar"><span>Mode</span><button className={mode === 'auto' ? 'selected' : ''} onClick={() => setMode('auto')}>Auto</button><button className={mode === 'coding' ? 'selected' : ''} onClick={() => setMode('coding')}>Coding</button><button className={mode === 'math' ? 'selected' : ''} onClick={() => setMode('math')}>Math</button></div><div className="inputrow"><textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); } }} placeholder="Message HARVIX..." /><button className="send" onClick={() => send()} disabled={loading || !input.trim()}><Send size={18} /></button></div><small>HARVIX preserves your prompt and returns the requested output.</small></div>
    </main>
  </div>;
}

createRoot(document.getElementById('root')).render(<App />);
