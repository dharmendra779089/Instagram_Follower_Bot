import os
import threading
from flask import Flask, render_template_string, jsonify, request
from main import run_bot, SIMILAR_ACCOUNT

app = Flask(__name__)

# Preset target accounts
PRESET_ACCOUNTS = ["chefsteps", "tasty", "gordonramsay", "jamie.oliver", "buzzfeedtasty"]

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
            max-width: 580px;
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

        /* ---------- Target Account Section ---------- */
        .section-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 12px;
        }

        .section-label::after {
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(255,255,255,0.08);
        }

        /* Preset chips */
        .chips-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }

        .chip {
            padding: 7px 14px;
            border-radius: 100px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(30,41,59,0.6);
            color: #cbd5e1;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }

        .chip:hover {
            border-color: #8b5cf6;
            color: #e2e8f0;
            background: rgba(139,92,246,0.12);
        }

        .chip.active {
            border-color: #8b5cf6;
            background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.25));
            color: #c4b5fd;
            box-shadow: 0 0 12px rgba(139,92,246,0.2);
        }

        /* Saved accounts dropdown */
        .dropdown-wrapper {
            position: relative;
            margin-bottom: 12px;
        }

        .dropdown-trigger {
            width: 100%;
            padding: 12px 40px 12px 16px;
            background: #1e293b;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            color: #f8fafc;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: left;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .dropdown-trigger:hover {
            border-color: rgba(139,92,246,0.4);
        }

        .dropdown-trigger.open {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 3px rgba(139,92,246,0.15);
            border-bottom-left-radius: 0;
            border-bottom-right-radius: 0;
        }

        .dropdown-arrow {
            transition: transform 0.2s ease;
            font-size: 0.7rem;
            color: #64748b;
        }

        .dropdown-trigger.open .dropdown-arrow {
            transform: rotate(180deg);
        }

        .dropdown-menu {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #1e293b;
            border: 1px solid rgba(139,92,246,0.3);
            border-top: none;
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 50;
            display: none;
        }

        .dropdown-menu.visible {
            display: block;
            animation: slideDown 0.15s ease;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-4px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .dropdown-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 16px;
            cursor: pointer;
            transition: background 0.15s ease;
            font-size: 0.875rem;
            color: #cbd5e1;
        }

        .dropdown-item:hover {
            background: rgba(139,92,246,0.12);
            color: #f8fafc;
        }

        .dropdown-item .account-name {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .dropdown-item .account-name::before {
            content: '@';
            color: #64748b;
            font-weight: 600;
        }

        .dropdown-item .remove-btn {
            background: none;
            border: none;
            color: #64748b;
            cursor: pointer;
            font-size: 1rem;
            line-height: 1;
            padding: 2px 6px;
            border-radius: 6px;
            transition: all 0.15s ease;
        }

        .dropdown-item .remove-btn:hover {
            background: rgba(239,68,68,0.2);
            color: #f87171;
        }

        .dropdown-empty {
            padding: 14px 16px;
            color: #475569;
            font-size: 0.8rem;
            text-align: center;
            font-style: italic;
        }

        /* Custom account input row */
        .add-account-row {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
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
            flex: 1;
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
            padding: 12px 16px 12px 36px;
            background: #1e293b;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            color: #f8fafc;
            font-size: 0.9rem;
            font-weight: 500;
            outline: none;
            transition: all 0.2s ease;
        }

        .form-input:focus {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 3px rgba(139,92,246,0.25);
        }

        .btn-add {
            padding: 12px 18px;
            border: none;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, #10b981, #059669);
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(16,185,129,0.3);
        }

        .btn-add:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16,185,129,0.45);
        }

        /* Active target display */
        .active-target {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 16px;
            background: rgba(139,92,246,0.08);
            border: 1px solid rgba(139,92,246,0.2);
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 0.82rem;
            color: #c4b5fd;
        }

        .active-target strong {
            color: #e0d4ff;
        }

        .active-target .target-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #8b5cf6;
            box-shadow: 0 0 6px #8b5cf6;
        }

        .info-box {
            background: #1e293b;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.05);
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

        /* Toast notification */
        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(80px);
            background: #334155;
            color: #f1f5f9;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 500;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 100;
            pointer-events: none;
        }

        .toast.show {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        /* Scrollbar for dropdown */
        .dropdown-menu::-webkit-scrollbar {
            width: 6px;
        }

        .dropdown-menu::-webkit-scrollbar-track {
            background: transparent;
        }

        .dropdown-menu::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 3px;
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

        <!-- Quick-select preset chips -->
        <div class="section-label">Quick Select</div>
        <div class="chips-row" id="chipsRow"></div>

        <!-- Saved accounts dropdown -->
        <div class="section-label">Saved Accounts</div>
        <div class="dropdown-wrapper" id="dropdownWrapper">
            <button class="dropdown-trigger" id="dropdownTrigger" onclick="toggleDropdown()">
                <span id="dropdownLabel">Select a saved account…</span>
                <span class="dropdown-arrow">▼</span>
            </button>
            <div class="dropdown-menu" id="dropdownMenu"></div>
        </div>

        <!-- Add custom account -->
        <div class="add-account-row">
            <div class="input-wrapper">
                <span class="input-prefix">@</span>
                <input type="text" id="customAccountInput" class="form-input" placeholder="Add new account…">
            </div>
            <button class="btn-add" onclick="addCustomAccount()">+ Save</button>
        </div>

        <!-- Active target indicator -->
        <div class="active-target" id="activeTargetBar">
            <span class="target-dot"></span>
            Target: <strong id="activeTargetName">{{ default_account }}</strong>
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

    <div class="toast" id="toast"></div>

    <script>
        // ---- State ----
        const PRESETS = {{ presets | tojson }};
        const STORAGE_KEY = 'igbot_saved_accounts';
        let selectedTarget = '{{ default_account }}';
        let savedAccounts = [];
        let dropdownOpen = false;
        let isPolling = false;

        // ---- Init ----
        function init() {
            loadSavedAccounts();
            renderChips();
            renderDropdown();
            setTarget(selectedTarget);
            pollStatus();

            // Close dropdown on outside click
            document.addEventListener('click', (e) => {
                const wrapper = document.getElementById('dropdownWrapper');
                if (!wrapper.contains(e.target)) closeDropdown();
            });

            // Enter key on custom input
            document.getElementById('customAccountInput').addEventListener('keydown', (e) => {
                if (e.key === 'Enter') addCustomAccount();
            });
        }

        // ---- Persistence ----
        function loadSavedAccounts() {
            try {
                savedAccounts = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
            } catch { savedAccounts = []; }
        }

        function persistSavedAccounts() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(savedAccounts));
        }

        // ---- Chips ----
        function renderChips() {
            const row = document.getElementById('chipsRow');
            row.innerHTML = '';
            PRESETS.forEach(name => {
                const chip = document.createElement('button');
                chip.className = 'chip' + (name === selectedTarget ? ' active' : '');
                chip.textContent = '@' + name;
                chip.onclick = () => setTarget(name);
                row.appendChild(chip);
            });
        }

        // ---- Dropdown ----
        function toggleDropdown() {
            dropdownOpen ? closeDropdown() : openDropdown();
        }

        function openDropdown() {
            dropdownOpen = true;
            document.getElementById('dropdownTrigger').classList.add('open');
            document.getElementById('dropdownMenu').classList.add('visible');
        }

        function closeDropdown() {
            dropdownOpen = false;
            document.getElementById('dropdownTrigger').classList.remove('open');
            document.getElementById('dropdownMenu').classList.remove('visible');
        }

        function renderDropdown() {
            const menu = document.getElementById('dropdownMenu');
            const label = document.getElementById('dropdownLabel');
            menu.innerHTML = '';

            if (savedAccounts.length === 0) {
                menu.innerHTML = '<div class="dropdown-empty">No saved accounts yet — add one below.</div>';
                label.textContent = 'Select a saved account…';
                return;
            }

            const isSavedSelected = savedAccounts.includes(selectedTarget);
            label.textContent = isSavedSelected ? ('@' + selectedTarget) : 'Select a saved account…';

            savedAccounts.forEach(name => {
                const item = document.createElement('div');
                item.className = 'dropdown-item';
                item.innerHTML = `
                    <span class="account-name">${name}</span>
                    <button class="remove-btn" title="Remove" onclick="event.stopPropagation(); removeAccount('${name}')">✕</button>
                `;
                item.onclick = () => { setTarget(name); closeDropdown(); };
                menu.appendChild(item);
            });
        }

        // ---- Add / Remove ----
        function addCustomAccount() {
            const input = document.getElementById('customAccountInput');
            let name = input.value.trim().replace(/^@/, '');
            if (!name) return;
            name = name.toLowerCase();

            if (savedAccounts.includes(name)) {
                showToast('Account @' + name + ' is already saved.');
                setTarget(name);
                input.value = '';
                return;
            }

            savedAccounts.unshift(name);
            persistSavedAccounts();
            renderDropdown();
            setTarget(name);
            input.value = '';
            showToast('Saved @' + name);
        }

        function removeAccount(name) {
            savedAccounts = savedAccounts.filter(a => a !== name);
            persistSavedAccounts();
            renderDropdown();
            showToast('Removed @' + name);
        }

        // ---- Selection ----
        function setTarget(name) {
            selectedTarget = name;
            document.getElementById('activeTargetName').textContent = name;
            renderChips();
            renderDropdown();
        }

        // ---- Toast ----
        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2200);
        }

        // ---- Bot execution ----
        async function startBot() {
            const btn = document.getElementById('runBtn');
            const targetAccount = selectedTarget || '{{ default_account }}';

            btn.disabled = true;
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
                    document.getElementById('runBtn').disabled = false;
                    document.getElementById('runBtn').innerText = 'Run Follower Bot Now';
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

        // Boot
        init();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        default_account=SIMILAR_ACCOUNT,
        presets=PRESET_ACCOUNTS
    )

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
