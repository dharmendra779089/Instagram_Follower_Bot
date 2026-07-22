import os
import threading
from flask import Flask, render_template_string, jsonify, request
from main import run_bot, SIMILAR_ACCOUNT

app = Flask(__name__)

# Execution state management
execution_status = {
    "status": "idle",  # idle, running, completed, error
    "message": "Ready to run Instagram Follower Bot.",
    "target_account": SIMILAR_ACCOUNT
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Follower Bot - Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background: #0f172a;
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 540px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 28px;
        }

        .icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #ec4899, #8b5cf6, #3b82f6);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        h1 {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #f43f5e, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 0.875rem;
            color: #94a3b8;
            margin-top: 4px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-label {
            display: block;
            font-size: 0.875rem;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 8px;
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-prefix {
            position: absolute;
            left: 16px;
            color: #64748b;
            font-weight: 600;
            font-size: 1rem;
            pointer-events: none;
        }

        .form-input {
            width: 100%;
            padding: 14px 16px 14px 36px;
            background: #1e293b;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 500;
            outline: none;
            transition: all 0.2s ease;
        }

        .form-input:focus {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25);
        }

        .info-box {
            background: #1e293b;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.875rem;
        }

        .info-row:last-child {
            margin-bottom: 0;
        }

        .info-label {
            color: #64748b;
        }

        .info-value {
            color: #e2e8f0;
            font-weight: 600;
        }

        .btn {
            width: 100%;
            padding: 14px 24px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
        }

        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .status-card {
            margin-top: 24px;
            padding: 16px 20px;
            border-radius: 12px;
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .status-idle { background: rgba(51, 65, 85, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); color: #cbd5e1; }
        .status-running { background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); color: #93c5fd; }
        .status-completed { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }
        .status-error { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }

        .spinner {
            width: 18px;
            height: 18px;
            border: 2px solid currentColor;
            border-bottom-color: transparent;
            border-radius: 50%;
            animation: rotation 1s linear infinite;
            display: inline-block;
            flex-shrink: 0;
        }

        @keyframes rotation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>

    <div class="card">
        <div class="header">
            <div class="icon">🤖</div>
            <div>
                <h1>Instagram Follower Bot</h1>
                <div class="subtitle">Cloud Selenium Automation Service</div>
            </div>
        </div>

        <div class="form-group">
            <label class="form-label" for="targetAccount">Target Account Handle</label>
            <div class="input-wrapper">
                <span class="input-prefix">@</span>
                <input type="text" id="targetAccount" class="form-input" value="{{ default_account }}" placeholder="Enter username (e.g. chefsteps)">
            </div>
        </div>

        <div class="info-box">
            <div class="info-row">
                <span class="info-label">Environment</span>
                <span class="info-value">Headless Chromium (Render Docker)</span>
            </div>
        </div>

        <button id="runBtn" class="btn" onclick="startBot()">Run Follower Bot Now</button>

        <div id="statusContainer" class="status-card status-idle">
            <span id="statusText">Ready to run Instagram Follower Bot.</span>
        </div>
    </div>

    <script>
        let isPolling = false;

        async function startBot() {
            const btn = document.getElementById('runBtn');
            const targetInput = document.getElementById('targetAccount');
            const targetAccount = targetInput.value.trim() || 'chefsteps';

            btn.disabled = true;
            targetInput.disabled = true;
            btn.innerText = 'Initializing Bot...';

            try {
                const res = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ target_account: targetAccount })
                });
                const data = await res.json();
                updateUI(data.status, data.message);
                if (!isPolling) pollStatus();
            } catch (err) {
                updateUI('error', 'Failed to trigger bot request.');
                btn.disabled = false;
                targetInput.disabled = false;
                btn.innerText = 'Run Follower Bot Now';
            }
        }

        async function pollStatus() {
            isPolling = true;
            try {
                const res = await fetch('/status');
                const data = await res.json();
                updateUI(data.status, data.message);
                
                if (data.status === 'running') {
                    setTimeout(pollStatus, 1500);
                } else {
                    isPolling = false;
                    const btn = document.getElementById('runBtn');
                    const targetInput = document.getElementById('targetAccount');
                    btn.disabled = false;
                    targetInput.disabled = false;
                    btn.innerText = 'Run Follower Bot Now';
                }
            } catch (err) {
                isPolling = false;
            }
        }

        function updateUI(status, message) {
            const statusContainer = document.getElementById('statusContainer');
            const statusText = document.getElementById('statusText');
            
            statusContainer.className = 'status-card status-' + status;
            
            if (status === 'running') {
                statusText.innerHTML = '<span class="spinner"></span> ' + message;
            } else {
                statusText.innerText = message;
            }
        }

        // Initial status check
        pollStatus();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, default_account=SIMILAR_ACCOUNT)

def log_progress(msg):
    global execution_status
    execution_status["message"] = msg

def execute_bot_background(target):
    global execution_status
    execution_status["status"] = "running"
    execution_status["target_account"] = target
    execution_status["message"] = f"Initializing Chromium for target @{target}..."
    
    success, msg = run_bot(headless=True, target_account=target, log_callback=log_progress)
    
    if success:
        execution_status["status"] = "completed"
        execution_status["message"] = msg
    else:
        execution_status["status"] = "error"
        execution_status["message"] = msg

@app.route("/run", methods=["POST"])
def trigger_bot():
    global execution_status
    if execution_status["status"] == "running":
        return jsonify(execution_status)

    data = request.get_json(silent=True) or {}
    target = data.get("target_account", SIMILAR_ACCOUNT).strip() or SIMILAR_ACCOUNT

    thread = threading.Thread(target=execute_bot_background, args=(target,))
    thread.daemon = True
    thread.start()
    
    execution_status["status"] = "running"
    execution_status["target_account"] = target
    execution_status["message"] = f"Bot started for target @{target}."
    return jsonify(execution_status)

@app.route("/status")
def get_status():
    return jsonify(execution_status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
