// BirdQuest Dashboard JavaScript

// ===================================
// Global State
// ===================================
let currentFilter = 'all';

// ===================================
// Toast Notifications
// ===================================
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'toastSlideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===================================
// Habit Completion
// ===================================
async function completeHabit(habitId, isCustom = false) {
    const habitItem = document.querySelector(`[data-habit-id="${habitId}"]`);
    const checkBtn = habitItem?.querySelector('.check-btn');

    if (!habitItem || checkBtn?.disabled) return;

    try {
        const response = await fetch('/api/complete-habit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                habit_id: habitId,
                is_custom: isCustom
            }),
        });

        const data = await response.json();

        if (data.success) {
            // Update UI
            habitItem.classList.add('completed');
            checkBtn.classList.add('checked');
            checkBtn.disabled = true;

            // Update XP display
            updateXPDisplay(data.current_xp, data.xp_needed);

            // Update completed count
            updateCompletedCount();

            // Show XP toast
            showToast(`+${data.xp_earned} XP earned!`, 'success');

            // Check for level up
            if (data.leveled_up) {
                showLevelUp(data.level, data.seeds_earned);
                updateStatsDisplay(data.level, data.seeds);
            }
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Error completing habit:', error);
        showToast('Failed to complete habit. Please try again.', 'error');
    }
}

// ===================================
// XP Display Update
// ===================================
function updateXPDisplay(currentXP, xpNeeded) {
    const xpDisplay = document.getElementById('xp-display');
    const xpBar = document.getElementById('xp-bar');

    if (xpDisplay) {
        xpDisplay.textContent = `${currentXP} / ${xpNeeded} XP`;
    }

    if (xpBar) {
        const percentage = Math.min(100, (currentXP / xpNeeded) * 100);
        xpBar.style.width = `${percentage}%`;
    }
}

// ===================================
// Stats Display Update
// ===================================
function updateStatsDisplay(level, seeds) {
    const levelDisplay = document.getElementById('level-display');
    const seedsCount = document.getElementById('seeds-count');

    if (levelDisplay) {
        levelDisplay.textContent = level;
    }

    if (seedsCount) {
        seedsCount.textContent = seeds;
    }
}

// ===================================
// Completed Count Update
// ===================================
function updateCompletedCount() {
    const completedItems = document.querySelectorAll('.habit-item.completed');
    const countDisplay = document.getElementById('completed-count');

    if (countDisplay) {
        countDisplay.textContent = completedItems.length;
    }
}

// ===================================
// Level Up Notification
// ===================================
function showLevelUp(level, seedsEarned) {
    const notification = document.getElementById('level-up-notification');
    const newLevelSpan = document.getElementById('new-level');
    const seedsSpan = document.getElementById('seeds-earned');

    if (newLevelSpan) {
        newLevelSpan.textContent = `Level ${level}`;
    }

    if (seedsSpan) {
        seedsSpan.textContent = seedsEarned;
    }

    notification?.classList.add('active');

    // Play celebration sound (optional)
    // playSound('levelup');
}

function closeLevelUp() {
    const notification = document.getElementById('level-up-notification');
    notification?.classList.remove('active');

    // Refresh the page to update all stats
    location.reload();
}

// ===================================
// Add Habit Modal
// ===================================
function openAddHabitModal() {
    const modal = document.getElementById('add-habit-modal');
    modal?.classList.add('active');

    // Focus on the name input
    const nameInput = document.getElementById('habit-name');
    nameInput?.focus();
}

function closeAddHabitModal() {
    const modal = document.getElementById('add-habit-modal');
    modal?.classList.remove('active');

    // Reset form
    const form = document.getElementById('add-habit-form');
    form?.reset();
}

async function addHabit(event) {
    event.preventDefault();

    const name = document.getElementById('habit-name').value.trim();
    const xp = parseInt(document.getElementById('habit-xp').value);
    const category = document.getElementById('habit-category').value;

    if (!name) {
        showToast('Please enter a habit name', 'error');
        return;
    }

    try {
        const response = await fetch('/api/add-habit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, xp, category }),
        });

        const data = await response.json();

        if (data.success) {
            // Add habit to the list
            addHabitToList(data.habit);

            // Close modal
            closeAddHabitModal();

            // Show success message
            showToast('Custom habit added!', 'success');

            // Update total count
            updateTotalHabitsCount();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Error adding habit:', error);
        showToast('Failed to add habit. Please try again.', 'error');
    }
}

function addHabitToList(habit) {
    const habitsList = document.getElementById('habits-list');

    const habitHTML = `
        <div class="habit-item"
             data-habit-id="${habit.id}"
             data-category="${habit.category}"
             data-custom="true">
            <div class="habit-check">
                <button class="check-btn" onclick="completeHabit('${habit.id}', true)">
                    <span class="check-icon">✓</span>
                </button>
            </div>
            <div class="habit-content">
                <h3 class="habit-name">${habit.name}</h3>
                <div class="habit-meta">
                    <span class="habit-xp">+${habit.xp} XP</span>
                    <span class="habit-category">${capitalizeFirst(habit.category)}</span>
                </div>
            </div>
            <button class="habit-delete" onclick="deleteHabit('${habit.id}')" title="Delete habit">
                🗑️
            </button>
        </div>
    `;

    habitsList.insertAdjacentHTML('beforeend', habitHTML);

    // Apply current filter
    applyFilter(currentFilter);
}

function updateTotalHabitsCount() {
    const totalItems = document.querySelectorAll('.habit-item').length;
    const summaryValues = document.querySelectorAll('.summary-value');

    if (summaryValues.length > 1) {
        summaryValues[1].textContent = totalItems;
    }
}

// ===================================
// Delete Habit
// ===================================
async function deleteHabit(habitId) {
    if (!confirm('Are you sure you want to delete this habit?')) {
        return;
    }

    try {
        const response = await fetch('/api/delete-habit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ habit_id: habitId }),
        });

        const data = await response.json();

        if (data.success) {
            // Remove from DOM
            const habitItem = document.querySelector(`[data-habit-id="${habitId}"]`);
            habitItem?.remove();

            // Update counts
            updateCompletedCount();
            updateTotalHabitsCount();

            showToast('Habit deleted', 'info');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Error deleting habit:', error);
        showToast('Failed to delete habit. Please try again.', 'error');
    }
}

// ===================================
// Category Filter
// ===================================
function initCategoryFilters() {
    const filters = document.querySelectorAll('.category-filter');

    filters.forEach(filter => {
        filter.addEventListener('click', () => {
            // Update active state
            filters.forEach(f => f.classList.remove('active'));
            filter.classList.add('active');

            // Get category and filter
            const category = filter.dataset.category;
            currentFilter = category;
            applyFilter(category);
        });
    });
}

function applyFilter(category) {
    const habits = document.querySelectorAll('.habit-item');

    habits.forEach(habit => {
        const habitCategory = habit.dataset.category;
        const isCustom = habit.dataset.custom === 'true';

        if (category === 'all') {
            habit.style.display = 'flex';
        } else if (category === 'custom') {
            habit.style.display = isCustom ? 'flex' : 'none';
        } else {
            habit.style.display = habitCategory === category ? 'flex' : 'none';
        }
    });
}

// ===================================
// Stats Modal
// ===================================
function showStats() {
    const modal = document.getElementById('stats-modal');
    modal?.classList.add('active');

    // Fetch and display stats
    fetchStats();
}

function closeStatsModal() {
    const modal = document.getElementById('stats-modal');
    modal?.classList.remove('active');
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        // Update stats display
        document.getElementById('stats-streak').textContent = data.streak;
        document.getElementById('stats-level').textContent = data.level;
        document.getElementById('stats-seeds').textContent = data.seeds;

        // Calculate owned birds (count unique entries)
        const ownedBirds = document.querySelectorAll('.bird-card.owned').length || '-';
        document.getElementById('stats-birds').textContent = ownedBirds;

        // Render activity chart
        renderActivityChart(data.daily_completions);
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

function renderActivityChart(dailyCompletions) {
    const chart = document.getElementById('activity-chart');
    if (!chart) return;

    // Get last 7 days
    const days = [];
    const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        const dayOfWeek = dayLabels[date.getDay()];

        days.push({
            date: dateStr,
            label: dayOfWeek,
            count: dailyCompletions[dateStr] || 0
        });
    }

    // Find max for scaling
    const maxCount = Math.max(...days.map(d => d.count), 1);

    // Render bars
    chart.innerHTML = days.map(day => {
        const height = Math.max(5, (day.count / maxCount) * 80);
        return `
            <div class="activity-day">
                <div class="activity-bar" style="height: ${height}px;" title="${day.count} habits"></div>
                <div class="activity-day-label">${day.label}</div>
            </div>
        `;
    }).join('');
}

// ===================================
// Utility Functions
// ===================================
function capitalizeFirst(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Close modals on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeAddHabitModal();
        closeStatsModal();
        closeLevelUp();
    }
});

// Add CSS animation for toast slide out
const style = document.createElement('style');
style.textContent = `
    @keyframes toastSlideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);

// ===================================
// Initialize
// ===================================
document.addEventListener('DOMContentLoaded', () => {
    initCategoryFilters();
    updateCompletedCount();

    // Add form submit handler
    const addHabitForm = document.getElementById('add-habit-form');
    if (addHabitForm) {
        addHabitForm.addEventListener('submit', addHabit);
    }
});
