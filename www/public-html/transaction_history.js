// transaction_history.js - Handles transaction history display with FastAPI backend

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global variables
let currentUser = null;
let transactions = [];
let currentTransaction = null;
let accessToken = null;

// Initialize page on load
document.addEventListener('DOMContentLoaded', function () {
    // Check if user is logged in
    const userData = sessionStorage.getItem('user');
    accessToken = sessionStorage.getItem('access_token');

    if (!userData || !accessToken) {
        // Redirect to login if not logged in
        window.location.href = 'login.html';
        return;
    }

    // Parse and store user data
    currentUser = JSON.parse(userData);

    // Load user information
    loadUserInformation();

    // Load transactions
    loadTransactions();
});

// Load user information into header
function loadUserInformation() {
    document.getElementById('headerUserName').textContent = currentUser.full_name;
    document.getElementById('headerBalance').textContent = formatCurrency(currentUser.available_balance);
}

// Load transactions from FastAPI backend
async function loadTransactions() {
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const transactionsList = document.getElementById('transactionsList');

    // Show loading state
    loadingState.style.display = 'block';
    emptyState.style.display = 'none';
    transactionsList.innerHTML = '';

    try {
        // Fetch transactions from backend
        const response = await fetch(`${API_BASE_URL}/transactions/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        // Hide loading state
        loadingState.style.display = 'none';

        if (response.ok) {
            const data = await response.json();
            
            // Check if data is an array or has a transactions property
            transactions = Array.isArray(data) ? data : (data.transactions || []);

            if (transactions.length === 0) {
                // Show empty state
                emptyState.style.display = 'block';
            } else {
                // Sort transactions by date (newest first)
                transactions.sort((a, b) => 
                    new Date(b.completed_at || b.initiated_at) - new Date(a.completed_at || a.initiated_at)
                );
                
                // Display transactions
                displayTransactions(transactions);
            }
        } else {
            // Handle error response
            console.error('Failed to fetch transactions');
            emptyState.style.display = 'block';
        }

    } catch (error) {
        console.error('Error loading transactions:', error);
        loadingState.style.display = 'none';
        emptyState.style.display = 'block';
    }
}

// Display transactions in the list
function displayTransactions(transactions) {
    const transactionsList = document.getElementById('transactionsList');
    transactionsList.innerHTML = '';

    transactions.forEach(transaction => {
        const transactionItem = createTransactionItem(transaction);
        transactionsList.appendChild(transactionItem);
    });
}

// Create transaction item element
function createTransactionItem(transaction) {
    const item = document.createElement('div');
    item.className = 'transaction-item';
    item.onclick = () => showTransactionDetail(transaction);

    const statusClass = (transaction.status || 'PENDING').toLowerCase();
    const statusText = transaction.status || 'PENDING';
    const displayDate = transaction.completed_at || transaction.initiated_at;

    item.innerHTML = `
        <div class="transaction-header">
            <div>
                <div class="transaction-title">Tuition payment for ${transaction.receiver_name || transaction.receiver_id}</div>
                <div class="transaction-details">
                    <div class="transaction-info">
                        <strong>Student:</strong> ${transaction.receiver_name || transaction.receiver_id}
                    </div>
                    <div class="transaction-info">
                        <strong>Date:</strong> ${formatDateTime(displayDate)}
                    </div>
                    <div class="transaction-id">
                        ID: ${transaction.transaction_id || 'N/A'}
                    </div>
                </div>
            </div>
            <div>
                <div class="transaction-amount">-${formatCurrency(transaction.amount)}</div>
                <div class="transaction-status ${statusClass}">${statusText}</div>
            </div>
        </div>
    `;

    return item;
}

// Show transaction detail modal
function showTransactionDetail(transaction) {
    currentTransaction = transaction;

    // Populate modal with transaction details
    document.getElementById('detailTxnId').textContent = transaction.transaction_id || 'N/A';
    document.getElementById('detailStatus').textContent = transaction.status || 'PENDING';
    
    const displayDate = transaction.completed_at || transaction.initiated_at;
    document.getElementById('detailDateTime').textContent = formatDateTime(displayDate);

    document.getElementById('detailPayer').textContent = transaction.payer_name || currentUser.full_name;
    document.getElementById('detailStudentId').textContent = transaction.receiver_id;
    document.getElementById('detailStudentName').textContent = transaction.receiver_name || transaction.receiver_id;
    document.getElementById('detailAmount').textContent = formatCurrency(transaction.amount);

    document.getElementById('detailSemester').textContent = transaction.semester || 'N/A';
    document.getElementById('detailAcademicYear').textContent = transaction.academic_year || 'N/A';

    // Show modal
    document.getElementById('detailModal').style.display = 'block';
}

// Close detail modal
function closeDetailModal() {
    document.getElementById('detailModal').style.display = 'none';
    currentTransaction = null;
}

// Refresh transactions
async function refreshTransactions() {
    const refreshBtn = document.querySelector('.refresh-btn');
    const originalHTML = refreshBtn.innerHTML;

    try {
        // Disable button and show loading
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<span class="loading-spinner-large" style="width: 18px; height: 18px; border-width: 3px; margin: 0 8px 0 0;"></span> Refreshing...';

        // Reload transactions
        await loadTransactions();

    } catch (error) {
        console.error('Refresh error:', error);
    } finally {
        // Restore button
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = originalHTML;
    }
}

// Download receipt
function downloadReceipt() {
    if (!currentTransaction) {
        alert('No transaction selected');
        return;
    }

    const displayDate = currentTransaction.completed_at || currentTransaction.initiated_at;

    // Create receipt content
    const receiptContent = `
===========================================
        TUITION PAYMENT RECEIPT
===========================================

Transaction ID: ${currentTransaction.transaction_id || 'N/A'}
Date: ${formatDateTime(displayDate)}
Status: ${currentTransaction.status || 'PENDING'}

-------------------------------------------
PAYER INFORMATION
-------------------------------------------
Name: ${currentTransaction.payer_name || currentUser.full_name}

-------------------------------------------
STUDENT INFORMATION
-------------------------------------------
Student ID: ${currentTransaction.receiver_id}
Student Name: ${currentTransaction.receiver_name || currentTransaction.receiver_id}

-------------------------------------------
PAYMENT DETAILS
-------------------------------------------
Semester: ${currentTransaction.semester || 'N/A'}
Academic Year: ${currentTransaction.academic_year || 'N/A'}
Amount: ${formatCurrency(currentTransaction.amount)}

-------------------------------------------
This is an official receipt for tuition payment.
Generated on: ${formatDateTime(new Date().toISOString())}
===========================================
    `;

    // Create blob and download
    const blob = new Blob([receiptContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `receipt_${currentTransaction.transaction_id || Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    // Show success message
    alert('Receipt downloaded successfully!');
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Format date and time
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);

    const dateOptions = {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    };

    const timeOptions = {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    };

    const dateStr = date.toLocaleDateString('en-GB', dateOptions);
    const timeStr = date.toLocaleTimeString('en-GB', timeOptions);

    return `${timeStr} ${dateStr}`;
}

// Logout function
function logout() {
    sessionStorage.clear();
    window.location.href = 'login.html';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('detailModal');
    if (event.target === modal) {
        closeDetailModal();
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', function (event) {
    // Close modal with Escape key
    if (event.key === 'Escape') {
        const modal = document.getElementById('detailModal');
        if (modal.style.display === 'block') {
            closeDetailModal();
        }
    }

    // Refresh with F5 or Ctrl+R (but use custom refresh)
    if (event.key === 'F5' || (event.ctrlKey && event.key === 'r')) {
        event.preventDefault();
        refreshTransactions();
    }
});