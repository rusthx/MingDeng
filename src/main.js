// MingDeng Frontend JavaScript
// API Base URL (overwritten when running inside Tauri)
let API_BASE = 'http://127.0.0.1:8765';

// Global state
let currentPage = 'calendar';
let currentPlan = null;
let calendarView = 'week'; // 'week' or 'month'
let currentDate = new Date();
let allTasks = {}; // Cache for tasks by date

// ============ Utility Functions ============

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.textContent = message;
    toast.classList.remove('hidden', 'bg-green-500', 'bg-red-500', 'bg-blue-500');

    if (type === 'success') {
        toast.classList.add('bg-green-500');
    } else if (type === 'error') {
        toast.classList.add('bg-red-500');
    } else {
        toast.classList.add('bg-blue-500');
    }

    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// ============ 安全工具，转义用户数据插入==========

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function safeHref(url) {
    if (!url) return '#';
    const clean = String(url).trim();
    const allowed = /^(https?|mailto):/i;
    return allowed.test(clean) ? clean : '#';
}

async function initializeApiBase() {
    console.log('[Tauri] Checking APIs. __TAURI__:', !!window.__TAURI__, '__TAURI_INTERNALS__:', !!window.__TAURI_INTERNALS__);
    const tauriInvoke = window.__TAURI__?.core?.invoke || window.__TAURI_INTERNALS__?.invoke;
    console.log('[Tauri] tauriInvoke available:', !!tauriInvoke);

    if (!tauriInvoke) {
        console.log('[Tauri] Not running in Tauri, using default API_BASE:', API_BASE);
        return;
    }

    showToast('正在启动本地后端...', 'info');
    try {
        const origin = await tauriInvoke('ensure_backend');
        console.log('[Tauri] ensure_backend returned:', origin, 'type:', typeof origin);
        if (origin && typeof origin === 'string') {
            API_BASE = origin;
            console.log('[Tauri] API_BASE updated to:', API_BASE);
            showToast('本地后端已启动', 'success');
            return;
        }
        console.warn('[Tauri] ensure_backend returned invalid origin:', origin);
    } catch (error) {
        console.error('[Tauri] Failed to start backend:', error);
        const detail = typeof error === 'string' ? error : (error?.message || JSON.stringify(error));
        showToast(`启动本地后端失败: ${detail}`, 'error');
    }
    console.log('[Tauri] API_BASE remains:', API_BASE);
}

async function apiCall(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE}${endpoint}`;
    try {
        const options = {
            method,
        };

        if (body) {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(body);
        }

        console.log(`[API] ${method} ${url}`, body || '');
        const response = await fetch(url, options);
        console.log(`[API] ${method} ${url} -> ${response.status}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error(`[API] ${method} ${url} failed:`, error);
        // 诊断：区分 CORS 阻断还是网络层阻断
        let diagnostic = '';
        try {
            await fetch(url, { mode: 'no-cors', method: 'GET' });
            diagnostic = '（CORS 策略阻止了请求，后端已收到连接）';
        } catch (e) {
            diagnostic = '（网络层无法连接到后端）';
        }
        console.error(`[API] Diagnostic for ${url}: ${diagnostic}`);
        showToast(`错误: ${error.message} ${diagnostic}`, 'error');
        throw error;
    }
}

// ============ Page Navigation ============

async function navigateToPage(pageName) {
    currentPage = pageName;

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageName) {
            link.classList.add('active');
        }
    });

    // Load page content
    const pageContainer = document.getElementById('page-container');
    try {
        const response = await fetch(`pages/${pageName}.html`);
        const html = await response.text();
        pageContainer.innerHTML = html;

        // Initialize page-specific logic
        initializePage(pageName);
    } catch (error) {
        pageContainer.innerHTML = `<div class="p-8 text-center text-red-500">页面加载失败: ${error.message}</div>`;
    }
}

function initializePage(pageName) {
    switch (pageName) {
        case 'calendar':
            initCalendarPage();
            break;
        case 'today':
            initTodayPage();
            break;
        case 'plan':
            initPlanPage();
            break;
        case 'stats':
            initStatsPage();
            break;
        case 'settings':
            initSettingsPage();
            break;
        case 'library':
            initLibraryPage();
            break;
    }
}

// ============ Today Page ============

async function initTodayPage() {
    // Set today's date
    const today = new Date();
    const dateString = today.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    });
    document.getElementById('today-date').textContent = `📅 ${dateString}`;

    // Set default date for add task modal
    const dateInput = document.getElementById('new-task-date');
    if (dateInput) {
        dateInput.value = today.toISOString().split('T')[0];
    }

    // Load tasks
    await loadTodayTasks();

    // Event listeners
    document.getElementById('refresh-tasks')?.addEventListener('click', loadTodayTasks);
    document.getElementById('add-task-btn')?.addEventListener('click', openAddTaskModal);
    document.getElementById('cancel-task-btn')?.addEventListener('click', closeAddTaskModal);
    document.getElementById('save-task-btn')?.addEventListener('click', saveNewTask);
}

async function loadTodayTasks() {
    const container = document.getElementById('tasks-container');
    const emptyState = document.getElementById('empty-state');

    container.innerHTML = '<div class="text-center py-12 text-gray-500">加载中...</div>';

    try {
        const data = await apiCall('/api/today');
        const tasks = data.tasks || [];

        if (tasks.length === 0) {
            container.innerHTML = '';
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
            container.innerHTML = tasks.map(task => renderTaskCard(task)).join('');

            // Add event listeners to task checkboxes
            tasks.forEach(task => {
                const checkbox = document.getElementById(`task-${task.id}`);
                if (checkbox) {
                    checkbox.addEventListener('change', () => toggleTask(task.id, checkbox.checked));
                }
            });
        }
    } catch (error) {
        container.innerHTML = '<div class="text-center py-12 text-red-500">加载失败</div>';
    }
}

function renderTaskCard(task) {
    const difficultyIcons = {
        'simple': '🟢',
        'medium': '🟡',
        'hard': '🔴'
    };

    const difficultyText = {
        'simple': '简单',
        'medium': '中等',
        'hard': '困难'
    };

    const isCompleted = task.status === 'completed';
    const timeText = `${Math.floor(task.estimated_time / 60)}h ${task.estimated_time % 60}m`;

    return `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <div class="flex items-start gap-3">
                <input
                    type="checkbox"
                    id="task-${task.id}"
                    ${isCompleted ? 'checked' : ''}
                    class="mt-1 w-5 h-5 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
                >
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                        <h4 class="text-lg font-medium text-gray-900 dark:text-white ${isCompleted ? 'line-through text-gray-500' : ''}">
                            ${escapeHtml(task.task)}
                        </h4>
                        <span class="text-sm">${difficultyIcons[task.difficulty]} ${difficultyText[task.difficulty]}</span>
                        <span class="text-sm text-gray-500">${timeText}</span>
                    </div>
                    ${task.tags && task.tags.length > 0 ? `
                        <div class="flex gap-1 flex-wrap mt-2">
                            ${task.tags.map(tag => `<span class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded">${escapeHtml(tag)}</span>`).join('')}
                        </div>
                    ` : ''}
                    ${task.notes ? `
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">${escapeHtml(task.notes)}</p>
                    ` : ''}
                </div>
                <button class="text-red-500 hover:text-red-700" onclick="deleteTask('${escapeHtml(task.id)}')">
                    🗑️
                </button>
            </div>
        </div>
    `;
}

async function toggleTask(taskId, isCompleted) {
    try {
        const endpoint = isCompleted ? `/api/tasks/${taskId}/complete` : `/api/tasks/${taskId}/uncomplete`;
        await apiCall(endpoint, 'POST');
        showToast(isCompleted ? '任务已完成！' : '任务已取消完成', 'success');
    } catch (error) {
        // Reload to reset checkbox
        await loadTodayTasks();
    }
}

async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) return;

    try {
        await apiCall(`/api/tasks/${taskId}`, 'DELETE');
        showToast('任务已删除', 'success');
        await loadTodayTasks();
    } catch (error) {
        // Error already shown by apiCall
    }
}

function openAddTaskModal() {
    document.getElementById('add-task-modal').classList.remove('hidden');
}

function closeAddTaskModal() {
    document.getElementById('add-task-modal').classList.add('hidden');
}

async function saveNewTask() {
    const title = document.getElementById('new-task-title').value.trim();
    const date = document.getElementById('new-task-date').value;
    const time = parseInt(document.getElementById('new-task-time').value);
    const difficulty = document.getElementById('new-task-difficulty').value;

    if (!title) {
        showToast('请输入任务描述', 'error');
        return;
    }

    if (!date) {
        showToast('请选择日期', 'error');
        return;
    }

    // Get or create a default plan
    try {
        const plansData = await apiCall('/api/plans');
        let planId;

        if (plansData.plans.length === 0) {
            // Create a default plan
            const newPlan = {
                name: '快速添加任务',
                tasks: []
            };
            // We need to use todo_manager directly, but for simplicity, we'll use the first available plan or create one
            // For now, show error
            showToast('请先创建一个学习计划', 'error');
            return;
        } else {
            planId = plansData.plans[0].id;
        }

        const taskData = {
            plan_id: planId,
            task: title,
            date: date,
            estimated_time: time,
            difficulty: difficulty
        };

        await apiCall('/api/tasks', 'POST', taskData);
        showToast('任务已添加', 'success');
        closeAddTaskModal();

        // Clear form
        document.getElementById('new-task-title').value = '';
        document.getElementById('new-task-time').value = '60';

        // Reload if on today's date
        await loadTodayTasks();
    } catch (error) {
        // Error already shown
    }
}

// ============ Plan Page ============

async function initPlanPage() {
    // Restore saved input from sessionStorage
    const savedGoals = sessionStorage.getItem('plan-learning-goals');
    const savedDate = sessionStorage.getItem('plan-start-date');

    const learningGoalsInput = document.getElementById('learning-goals');
    const startDateInput = document.getElementById('start-date');

    if (learningGoalsInput && savedGoals) {
        learningGoalsInput.value = savedGoals;
    }

    if (startDateInput) {
        startDateInput.value = savedDate || new Date().toISOString().split('T')[0];
    }

    // Auto-save input to sessionStorage
    learningGoalsInput?.addEventListener('input', (e) => {
        sessionStorage.setItem('plan-learning-goals', e.target.value);
    });

    startDateInput?.addEventListener('change', (e) => {
        sessionStorage.setItem('plan-start-date', e.target.value);
    });

    // Load existing plans
    await loadExistingPlans();

    // Event listeners
    document.getElementById('generate-plan-btn')?.addEventListener('click', generatePlan);
    document.getElementById('save-plan-btn')?.addEventListener('click', savePlan);
    document.getElementById('regenerate-plan-btn')?.addEventListener('click', regeneratePlan);
}

async function generatePlan() {
    const userInput = document.getElementById('learning-goals').value.trim();
    const startDate = document.getElementById('start-date').value;

    if (!userInput) {
        showToast('请输入学习目标', 'error');
        return;
    }

    const generateBtn = document.getElementById('generate-plan-btn');
    const generatingState = document.getElementById('generating-state');
    const planPreview = document.getElementById('plan-preview');

    generateBtn.disabled = true;
    generatingState.classList.remove('hidden');
    planPreview.classList.add('hidden');

    try {
        const data = await apiCall('/api/plan/generate', 'POST', {
            user_input: userInput,
            start_date: startDate
        });

        if (data.success) {
            currentPlan = data.plan;
            displayPlanPreview(data.plan);
            showToast('计划生成成功！', 'success');
        }
    } catch (error) {
        // Error already shown
    } finally {
        generateBtn.disabled = false;
        generatingState.classList.add('hidden');
    }
}

function displayPlanPreview(plan) {
    const planPreview = document.getElementById('plan-preview');
    const planName = document.getElementById('plan-name');
    const planTasksPreview = document.getElementById('plan-tasks-preview');

    planName.textContent = plan.name;

    const tasksHTML = plan.tasks.map(task => `
        <div class="p-3 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <span class="font-medium text-gray-900 dark:text-white">${escapeHtml(task.task)}</span>
                    <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        📅 ${escapeHtml(task.date)} | ⏱️ ${task.estimated_time}分钟 | ${getDifficultyIcon(task.difficulty)} ${escapeHtml(task.difficulty)}
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    planTasksPreview.innerHTML = tasksHTML;
    planPreview.classList.remove('hidden');
}

function getDifficultyIcon(difficulty) {
    const icons = { 'simple': '🟢', 'medium': '🟡', 'hard': '🔴' };
    return icons[difficulty] || '⚪';
}

async function savePlan() {
    if (!currentPlan) {
        showToast('没有可保存的计划', 'error');
        return;
    }

    showToast('计划已保存到日历', 'success');
    document.getElementById('plan-preview').classList.add('hidden');
    document.getElementById('learning-goals').value = '';
    currentPlan = null;

    // Clear saved input from sessionStorage
    sessionStorage.removeItem('plan-learning-goals');
    sessionStorage.removeItem('plan-start-date');

    await loadExistingPlans();
}

async function regeneratePlan() {
    // Re-trigger generation
    await generatePlan();
}

async function loadExistingPlans() {
    const container = document.getElementById('existing-plans');

    try {
        const data = await apiCall('/api/plans');
        const plans = data.plans || [];

        if (plans.length === 0) {
            container.innerHTML = '<div class="col-span-2 text-center py-8 text-gray-500 dark:text-gray-400">暂无计划</div>';
        } else {
            container.innerHTML = plans.map(plan => `
                <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                    <h4 class="font-semibold text-gray-900 dark:text-white mb-2">${escapeHtml(plan.name)}</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        共 ${plan.tasks.length} 个任务
                    </p>
                    <button class="text-sm text-red-500 hover:text-red-700" onclick="deletePlan('${escapeHtml(plan.id)}')">
                        删除计划
                    </button>
                </div>
            `).join('');
        }
    } catch (error) {
        container.innerHTML = '<div class="col-span-2 text-center py-8 text-red-500">加载失败</div>';
    }
}

async function deletePlan(planId) {
    if (!confirm('确定要删除这个计划吗？这将删除所有相关任务。')) return;

    try {
        await apiCall(`/api/plans/${planId}`, 'DELETE');
        showToast('计划已删除', 'success');
        await loadExistingPlans();
    } catch (error) {
        // Error already shown
    }
}

// ============ Stats Page ============

async function initStatsPage() {
    await loadStats();
}

async function loadStats() {
    try {
        const data = await apiCall('/api/stats');
        const stats = data.stats;

        // Update total stats
        document.getElementById('stat-total').textContent = stats.total_tasks;
        document.getElementById('stat-completed').textContent = stats.completed;
        document.getElementById('stat-rate').textContent = `${stats.completion_rate}%`;

        // Update difficulty stats
        ['simple', 'medium', 'hard'].forEach(difficulty => {
            const diffData = stats.by_difficulty[difficulty];
            const completed = diffData.completed;
            const total = diffData.total;
            const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

            document.getElementById(`difficulty-${difficulty}-completed`).textContent = completed;
            document.getElementById(`difficulty-${difficulty}-total`).textContent = total;
            document.getElementById(`difficulty-${difficulty}-bar`).style.width = `${percentage}%`;
        });
    } catch (error) {
        // Error already shown
    }
}

// ============ Settings Page ============

async function initSettingsPage() {
    await loadConfig();

    // Event listeners
    document.getElementById('save-api-config')?.addEventListener('click', saveAPIConfig);
    document.getElementById('save-user-config')?.addEventListener('click', saveUserConfig);
    document.getElementById('create-backup')?.addEventListener('click', createBackup);
    document.getElementById('view-backups')?.addEventListener('click', viewBackups);
    document.getElementById('clear-memory')?.addEventListener('click', clearMemory);
}

async function loadConfig() {
    try {
        const data = await apiCall('/api/config');

        document.getElementById('api-base-url').value = data.api.base_url;
        document.getElementById('api-key').value = '';  // Don't show API key
        document.getElementById('api-key').placeholder = data.api.api_key;
        document.getElementById('api-model').value = data.api.model;
        document.getElementById('user-name').value = data.user.name;
        document.getElementById('user-timezone').value = data.user.timezone;
    } catch (error) {
        // Error already shown
    }
}

async function saveAPIConfig() {
    const baseUrl = document.getElementById('api-base-url').value.trim();
    const apiKey = document.getElementById('api-key').value.trim();
    const model = document.getElementById('api-model').value.trim();

    if (!baseUrl || !model) {
        showToast('请填写完整信息', 'error');
        return;
    }

    try {
        const payload = {
            base_url: baseUrl,
            model: model
        };

        if (apiKey) {
            payload.api_key = apiKey;
        }

        await apiCall('/api/config', 'POST', payload);
        showToast('API 配置已保存', 'success');

        // Clear API key input
        document.getElementById('api-key').value = '';
    } catch (error) {
        // Error already shown
    }
}

async function saveUserConfig() {
    const userName = document.getElementById('user-name').value.trim();
    const timezone = document.getElementById('user-timezone').value;

    try {
        await apiCall('/api/config', 'POST', {
            user_name: userName,
            timezone: timezone
        });
        showToast('用户设置已保存', 'success');
    } catch (error) {
        // Error already shown
    }
}

async function createBackup() {
    try {
        const data = await apiCall('/api/backup', 'POST', { reason: 'Manual backup' });
        if (data.success) {
            showToast('备份创建成功', 'success');
        }
    } catch (error) {
        // Error already shown
    }
}

async function viewBackups() {
    try {
        const data = await apiCall('/api/backups');
        const backups = data.backups || [];

        if (backups.length === 0) {
            showToast('暂无备份', 'info');
        } else {
            alert(`共有 ${backups.length} 个备份\n\n${backups.map(b => `${b.datetime} - ${b.reason}`).join('\n')}`);
        }
    } catch (error) {
        // Error already shown
    }
}

async function clearMemory() {
    if (!confirm('确定要清除 AI 记忆吗？这个操作不可恢复。')) return;

    showToast('AI 记忆已清除', 'success');
}

// ============ Library Page ============

async function initLibraryPage() {
    await loadResources();

    document.getElementById('add-resource-btn')?.addEventListener('click', addResource);
}

async function loadResources() {
    const container = document.getElementById('resources-list');

    try {
        const data = await apiCall('/api/resources');
        const resources = data.resources || [];

        if (resources.length === 0) {
            container.innerHTML = '<div class="text-center py-8 text-gray-500 dark:text-gray-400">暂无资源</div>';
        } else {
            container.innerHTML = resources.map(resource => `
                <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="text-lg">${getResourceTypeIcon(resource.type)}</span>
                                <span class="font-medium text-gray-900 dark:text-white">${escapeHtml(resource.description || '资源')}</span>
                            </div>
                            <a href="${safeHref(resource.content)}" target="_blank" class="text-sm text-blue-500 hover:underline break-all">
                                ${escapeHtml(resource.content)}
                            </a>
                            <div class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                添加于: ${new Date(resource.captured_at).toLocaleString('zh-CN')}
                            </div>
                        </div>
                        <button class="text-red-500 hover:text-red-700 ml-4" onclick="deleteResource('${escapeHtml(resource.id)}')">
                            🗑️
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        container.innerHTML = '<div class="text-center py-8 text-red-500">加载失败</div>';
    }
}

function getResourceTypeIcon(type) {
    const icons = {
        'video': '📹',
        'article': '📄',
        'paper': '📑',
        'other': '📌'
    };
    return icons[type] || '📌';
}

async function addResource() {
    const content = document.getElementById('resource-content').value.trim();
    const description = document.getElementById('resource-description').value.trim();
    const type = document.getElementById('resource-type').value;

    if (!content) {
        showToast('请输入资源链接或描述', 'error');
        return;
    }

    try {
        await apiCall('/api/resources', 'POST', {
            content,
            description,
            type,
            auto_link: true
        });

        showToast('资源已添加', 'success');

        // Clear inputs
        document.getElementById('resource-content').value = '';
        document.getElementById('resource-description').value = '';

        await loadResources();
    } catch (error) {
        // Error already shown
    }
}

async function deleteResource(resourceId) {
    if (!confirm('确定要删除这个资源吗？')) return;

    try {
        await apiCall(`/api/resources/${resourceId}`, 'DELETE');
        showToast('资源已删除', 'success');
        await loadResources();
    } catch (error) {
        // Error already shown
    }
}

// ============ Calendar Page ============

async function initCalendarPage() {
    // Restore saved view preference
    const savedView = sessionStorage.getItem('calendar-view');
    if (savedView === 'week' || savedView === 'month') {
        calendarView = savedView;
    } else {
        // Default to week view
        calendarView = 'week';
    }

    currentDate = new Date();

    // Load tasks first
    await loadAllPlansTasks();

    // Initialize view buttons and containers with correct state
    // This must happen before renderCalendar
    initializeViewButtons();

    // Render calendar after view is properly set up
    renderCalendar();

    // Event listeners
    document.getElementById('view-week')?.addEventListener('click', () => switchView('week'));
    document.getElementById('view-month')?.addEventListener('click', () => switchView('month'));
    document.getElementById('prev-period')?.addEventListener('click', () => navigatePeriod(-1));
    document.getElementById('next-period')?.addEventListener('click', () => navigatePeriod(1));
    document.getElementById('today-btn')?.addEventListener('click', () => {
        currentDate = new Date();
        renderCalendar();
    });
    document.getElementById('close-modal')?.addEventListener('click', closeDayModal);
    document.getElementById('reschedule-btn')?.addEventListener('click', openRescheduleModal);
    document.getElementById('close-reschedule-modal')?.addEventListener('click', closeRescheduleModal);
    document.getElementById('reschedule-from-today')?.addEventListener('click', () => rescheduleTasksWithMode('from_today'));
    document.getElementById('reschedule-include-incomplete')?.addEventListener('click', () => rescheduleTasksWithMode('include_incomplete'));
}

function initializeViewButtons() {
    const weekBtn = document.getElementById('view-week');
    const monthBtn = document.getElementById('view-month');
    const weekView = document.getElementById('week-view');
    const monthView = document.getElementById('month-view');

    // Ensure all elements exist before proceeding
    if (!weekBtn || !monthBtn || !weekView || !monthView) {
        console.error('Calendar view elements not found');
        return;
    }

    if (calendarView === 'week') {
        // Week button active
        weekBtn.classList.add('bg-blue-500', 'text-white');
        weekBtn.classList.remove('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');

        // Month button inactive
        monthBtn.classList.remove('bg-blue-500', 'text-white');
        monthBtn.classList.add('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');

        // Show week view, hide month view
        weekView.classList.remove('hidden');
        monthView.classList.add('hidden');
    } else {
        // Month button active
        monthBtn.classList.add('bg-blue-500', 'text-white');
        monthBtn.classList.remove('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');

        // Week button inactive
        weekBtn.classList.remove('bg-blue-500', 'text-white');
        weekBtn.classList.add('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');

        // Show month view, hide week view
        monthView.classList.remove('hidden');
        weekView.classList.add('hidden');
    }
}

async function loadAllPlansTasks() {
    try {
        const data = await apiCall('/api/plans');
        const plans = data.plans || [];

        // Group tasks by date
        allTasks = {};
        plans.forEach(plan => {
            plan.tasks?.forEach(task => {
                const date = task.date;
                if (!allTasks[date]) {
                    allTasks[date] = [];
                }
                allTasks[date].push(task);
            });
        });
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function switchView(view) {
    calendarView = view;

    // Save view preference
    sessionStorage.setItem('calendar-view', view);

    const weekBtn = document.getElementById('view-week');
    const monthBtn = document.getElementById('view-month');
    const weekView = document.getElementById('week-view');
    const monthView = document.getElementById('month-view');

    if (view === 'week') {
        weekBtn.classList.add('bg-blue-500', 'text-white');
        weekBtn.classList.remove('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');
        monthBtn.classList.remove('bg-blue-500', 'text-white');
        monthBtn.classList.add('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');
        weekView.classList.remove('hidden');
        monthView.classList.add('hidden');
    } else {
        monthBtn.classList.add('bg-blue-500', 'text-white');
        monthBtn.classList.remove('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');
        weekBtn.classList.remove('bg-blue-500', 'text-white');
        weekBtn.classList.add('bg-gray-300', 'dark:bg-gray-600', 'text-gray-700', 'dark:text-gray-300');
        monthView.classList.remove('hidden');
        weekView.classList.add('hidden');
    }

    renderCalendar();
}

function navigatePeriod(direction) {
    if (calendarView === 'week') {
        currentDate.setDate(currentDate.getDate() + (direction * 7));
    } else {
        currentDate.setMonth(currentDate.getMonth() + direction);
    }
    renderCalendar();
}

function renderCalendar() {
    if (calendarView === 'week') {
        renderWeekView();
    } else {
        renderMonthView();
    }
    updateCalendarTitle();
}

function updateCalendarTitle() {
    const title = document.getElementById('calendar-title');
    const prevBtn = document.getElementById('prev-period');
    const nextBtn = document.getElementById('next-period');

    if (!title || !prevBtn || !nextBtn) {
        console.error('Calendar navigation elements not found');
        return;
    }

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth() + 1;

    if (calendarView === 'week') {
        const weekNum = getWeekNumber(currentDate);
        title.textContent = `${year}年${month}月 第${weekNum}周`;
        prevBtn.textContent = '← 上一周';
        nextBtn.textContent = '下一周 →';
    } else {
        title.textContent = `${year}年${month}月`;
        prevBtn.textContent = '← 上个月';
        nextBtn.textContent = '下个月 →';
    }
}

function getWeekNumber(date) {
    const firstDayOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
    const dayOfMonth = date.getDate();
    return Math.ceil((dayOfMonth + firstDayOfMonth.getDay()) / 7);
}

function renderWeekView() {
    const container = document.getElementById('week-view');
    if (!container) {
        console.error('Week view container not found');
        return;
    }

    const startOfWeek = getStartOfWeek(currentDate);

    let html = '';
    const weekDays = ['日', '一', '二', '三', '四', '五', '六'];

    for (let i = 0; i < 7; i++) {
        const day = new Date(startOfWeek);
        day.setDate(day.getDate() + i);
        const dateStr = formatDate(day);
        const tasks = allTasks[dateStr] || [];
        const isToday = formatDate(new Date()) === dateStr;

        html += `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border ${isToday ? 'border-blue-500' : 'border-gray-200 dark:border-gray-700'} cursor-pointer hover:shadow-md transition"
                 onclick="openDayDetail('${dateStr}')">
                <div class="text-center mb-3">
                    <div class="text-sm text-gray-500 dark:text-gray-400">周${weekDays[i]}</div>
                    <div class="text-2xl font-bold ${isToday ? 'text-blue-500' : 'text-gray-900 dark:text-white'}">${day.getDate()}</div>
                </div>
                <div class="space-y-2">
                    ${renderTasksSummary(tasks)}
                </div>
                ${tasks.length === 0 ? '<div class="text-center text-gray-400 dark:text-gray-500 text-sm py-4">无任务</div>' : ''}
            </div>
        `;
    }

    container.innerHTML = html;
}

function renderMonthView() {
    const container = document.getElementById('month-grid');
    if (!container) {
        console.error('Month view container not found');
        return;
    }

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    let html = '';
    const today = formatDate(new Date());

    for (let i = 0; i < 42; i++) { // 6 weeks
        const day = new Date(startDate);
        day.setDate(day.getDate() + i);
        const dateStr = formatDate(day);
        const tasks = allTasks[dateStr] || [];
        const isCurrentMonth = day.getMonth() === month;
        const isToday = today === dateStr;

        html += `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-2 min-h-[100px] border ${isToday ? 'border-blue-500' : 'border-gray-200 dark:border-gray-700'} ${!isCurrentMonth ? 'opacity-40' : ''} cursor-pointer hover:shadow-md transition"
                 onclick="openDayDetail('${dateStr}')">
                <div class="text-right mb-1">
                    <span class="text-sm font-semibold ${isToday ? 'text-blue-500' : isCurrentMonth ? 'text-gray-900 dark:text-white' : 'text-gray-400'}">${day.getDate()}</span>
                </div>
                <div class="space-y-1">
                    ${tasks.slice(0, 3).map(task => `
                        <div class="text-xs px-1 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded truncate" title="${escapeHtml(task.task)}">
                            ${getDifficultyIcon(task.difficulty)} ${escapeHtml(task.task)}
                        </div>
                    `).join('')}
                    ${tasks.length > 3 ? `<div class="text-xs text-gray-500 text-center">+${tasks.length - 3} 更多</div>` : ''}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

function renderTasksSummary(tasks) {
    if (tasks.length === 0) return '';

    return tasks.slice(0, 3).map(task => `
        <div class="text-sm px-2 py-1 bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded border border-blue-200 dark:border-blue-800 truncate"
             title="${escapeHtml(task.task)}">
            ${getDifficultyIcon(task.difficulty)} ${escapeHtml(task.task)}
        </div>
    `).join('') + (tasks.length > 3 ? `
        <div class="text-xs text-gray-500 dark:text-gray-400 text-center">
            +${tasks.length - 3} 个任务
        </div>
    ` : '');
}

function getDifficultyIcon(difficulty) {
    const icons = { 'simple': '🟢', 'medium': '🟡', 'hard': '🔴' };
    return icons[difficulty] || '⚪';
}

function getStartOfWeek(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day;
    return new Date(d.setDate(diff));
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function openDayDetail(dateStr) {
    const modal = document.getElementById('day-detail-modal');
    const titleEl = document.getElementById('modal-date-title');
    const tasksContainer = document.getElementById('modal-tasks-container');
    const emptyState = document.getElementById('modal-empty-state');

    const date = new Date(dateStr);
    titleEl.textContent = `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;

    const tasks = allTasks[dateStr] || [];

    if (tasks.length === 0) {
        tasksContainer.classList.add('hidden');
        emptyState.classList.remove('hidden');
    } else {
        emptyState.classList.add('hidden');
        tasksContainer.classList.remove('hidden');
        tasksContainer.innerHTML = tasks.map(task => renderModalTask(task)).join('');
    }

    modal.classList.remove('hidden');
}

function renderModalTask(task) {
    const difficultyText = { 'simple': '简单', 'medium': '中等', 'hard': '困难' };
    const isCompleted = task.status === 'completed';
    const timeText = `${Math.floor(task.estimated_time / 60)}h ${task.estimated_time % 60}m`;

    return `
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
            <div class="flex items-start gap-3">
                <input
                    type="checkbox"
                    ${isCompleted ? 'checked' : ''}
                    class="mt-1 w-5 h-5 text-blue-500 rounded focus:ring-2 focus:ring-blue-500"
                    onchange="toggleTaskFromModal('${task.id}', this.checked)"
                >
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                        <h4 class="text-base font-medium ${isCompleted ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}">
                            ${escapeHtml(task.task)}
                        </h4>
                        <span class="text-sm">${getDifficultyIcon(task.difficulty)} ${difficultyText[task.difficulty]}</span>
                        <span class="text-sm text-gray-500">${timeText}</span>
                    </div>
                    ${task.tags && task.tags.length > 0 ? `
                        <div class="flex gap-1 flex-wrap mt-2">
                            ${task.tags.map(tag => `<span class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded">${escapeHtml(tag)}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

async function toggleTaskFromModal(taskId, isCompleted) {
    try {
        const endpoint = isCompleted ? `/api/tasks/${taskId}/complete` : `/api/tasks/${taskId}/uncomplete`;
        await apiCall(endpoint, 'POST');
        await loadAllPlansTasks();
        renderCalendar();
        showToast(isCompleted ? '任务已完成！' : '任务已取消完成', 'success');
    } catch (error) {
        await loadAllPlansTasks();
        renderCalendar();
    }
}

function closeDayModal() {
    document.getElementById('day-detail-modal').classList.add('hidden');
}

function openRescheduleModal() {
    document.getElementById('reschedule-modal').classList.remove('hidden');
}

function closeRescheduleModal() {
    document.getElementById('reschedule-modal').classList.add('hidden');
}

async function rescheduleTasksWithMode(mode) {
    // Close modal
    closeRescheduleModal();

    // Show loading
    const loadingEl = document.getElementById('reschedule-loading');
    loadingEl.classList.remove('hidden');

    try {
        const result = await apiCall('/api/plan/reschedule', 'POST', { mode });

        if (result.success) {
            showToast(`✓ ${result.message}`, 'success');

            // Show adjustment reason if available
            if (result.adjustment_reason) {
                setTimeout(() => {
                    showToast(`AI建议: ${result.adjustment_reason}`, 'info');
                }, 1500);
            }

            // Reload calendar
            await loadAllPlansTasks();
            renderCalendar();
        } else {
            showToast(result.message || '重排失败', 'error');
        }
    } catch (error) {
        // Error already shown by apiCall
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// ============ Chat Widget ============

function initChatWidget() {
    const chatToggle = document.getElementById('chat-toggle');
    const chatWidget = document.getElementById('chat-widget');
    const chatClose = document.getElementById('chat-close');
    const chatSend = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input');

    chatToggle.addEventListener('click', () => {
        chatWidget.classList.toggle('hidden');
        chatToggle.classList.toggle('hidden');
    });

    chatClose.addEventListener('click', () => {
        chatWidget.classList.add('hidden');
        chatToggle.classList.remove('hidden');
    });

    chatSend.addEventListener('click', sendChatMessage);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    const messagesContainer = document.getElementById('chat-messages');

    // Add user message
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'text-right';
    const userBubble = document.createElement('div');
    userBubble.className = 'inline-block bg-blue-500 text-white px-3 py-2 rounded-lg max-w-xs';
    userBubble.textContent = message;
    userMsgDiv.appendChild(userBubble);
    messagesContainer.appendChild(userMsgDiv);

    input.value = '';

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const data = await apiCall('/api/chat', 'POST', {
            message: message,
            stream: false
        });

        // Add AI response
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'text-left';
        const aiBubble = document.createElement('div');
        aiBubble.className = 'inline-block bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 rounded-lg max-w-xs';
        aiBubble.textContent = data.response;
        aiMsgDiv.appendChild(aiBubble);
        messagesContainer.appendChild(aiMsgDiv);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-center text-red-500 text-sm';
        errorDiv.textContent = '发送失败';
        messagesContainer.appendChild(errorDiv);
    }
}

// ============ Initialization ============

document.addEventListener('DOMContentLoaded', async () => {
    await initializeApiBase();

    // Setup navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            navigateToPage(page);
        });
    });

    // Setup backup button
    document.getElementById('backup-btn')?.addEventListener('click', createBackup);

    // Initialize chat widget
    initChatWidget();

    // Load initial page
    navigateToPage('calendar');
});
