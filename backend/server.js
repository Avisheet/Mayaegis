// Covert to django
const cors = require('cors');
const express = require('express');
const axios = require('axios');
const { PythonShell } = require('python-shell');
const dotenv = require('dotenv');
const app = express();
const port = 5000;

// Load environment variables from .env file
dotenv.config();

app.use(cors());
app.use(express.json());

// Validate required environment variables
// if (!process.env.OPENAI_API_KEY) {
//     console.error('Error: OPENAI_API_KEY is not set in .env file.');
//     process.exit(1);
// }

// Python path for the virtual environment (can be overridden via environment variable)
const pythonPath = process.env.PYTHON_PATH || '/root/venv/bin/python3';

// Endpoint to run agents
app.post('/api/run-agents', async (req, res) => {
    console.log("Received request at /api/run-agents");
    const { userQuestion } = req.body;

    if (!userQuestion) {
        return res.status(400).json({ error: 'userQuestion is required' });
    }

    const options = {
        pythonPath: pythonPath,
        scriptPath: __dirname,
        args: [userQuestion]
    };

    console.log("Running Python script with options:", options);

    PythonShell.run('run_agents.py', options, (err, results) => {
        if (err) {
            console.error("PythonShell error:", err);
            return res.status(500).json({ error: 'Failed to run agents', details: err.message });
        }
        try {
            const parsedResults = JSON.parse(results[0]);
            res.json(parsedResults);
        } catch (parseError) {
            console.error("Failed to parse Python script output:", parseError);
            res.status(500).json({ error: 'Failed to parse script output', details: parseError.message });
        }
    });
});

// Endpoint to check agent status
app.get('/api/agent-status/:id', async (req, res) => {
    const { id } = req.params;

    const options = {
        pythonPath: pythonPath,
        scriptPath: __dirname,
        args: [id]
    };

    PythonShell.run('check_agent_status.py', options, (err, results) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Failed to check agent status', details: err.message });
        }
        try {
            const parsedResults = JSON.parse(results[0]);
            res.json(parsedResults);
        } catch (parseError) {
            console.error("Failed to parse Python script output:", parseError);
            res.status(500).json({ error: 'Failed to parse script output', details: parseError.message });
        }
    });
});

// Endpoint to load agent content
app.post('/api/load-agent-content', async (req, res) => {
    const { paths } = req.body;

    if (!paths) {
        return res.status(400).json({ error: 'paths is required' });
    }

    const options = {
        pythonPath: pythonPath,
        scriptPath: __dirname,
        args: [JSON.stringify(paths)]
    };

    PythonShell.run('load_agent_content.py', options, (err, results) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Failed to load agent content', details: err.message });
        }
        try {
            const parsedResults = JSON.parse(results[0]);
            res.json(parsedResults);
        } catch (parseError) {
            console.error("Failed to parse Python script output:", parseError);
            res.status(500).json({ error: 'Failed to parse script output', details: parseError.message });
        }
    });
});

// Endpoint to handle chat with OpenAI
app.post('/api/chat', async (req, res) => {
    const { messages, model } = req.body;

    if (!messages || !model) {
        return res.status(400).json({ error: 'messages and model are required' });
    }

    try {
        const response = await axios.post('https://api.openai.com/v1/chat/completions', {
            model: model,
            messages: messages,
            stream: true
        }, {
            headers: {
                'Authorization': ``
            }
        });

        res.json(response.data);
    } catch (error) {
        console.error('Error calling OpenAI API:', error);
        res.status(500).json({ error: 'Failed to get response from OpenAI', details: error.message });
    }
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Server running on port ${port}`);
});