// payment_form.js - Handles tuition payment form logic with FastAPI backend

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global variables
let currentUser = null;
let currentStudent = null;
let otpTimerInterval = null;
let otpResendTimerInterval = null;
let accessToken = null;
let transaction_id = null;

// Initialize page on load
document.addEventListener('DOMContentLoaded', function () {
    console.log('=== PAYMENT FORM PAGE LOADED ===');
    
    // Check if user is logged in
    const userData = sessionStorage.getItem('user');
    accessToken = sessionStorage.getItem('access_token');

    console.log('User data from session:', userData);
    console.log('Access token exists:', !!accessToken);

    if (!userData || !accessToken) {
        // Redirect to login if not logged in
        console.log('No user data or token found, redirecting to login...');
        window.location.href = './login.html';
        return;
    }

    // Parse and store user data
    currentUser = JSON.parse(userData);
    console.log('Current user:', currentUser);

    // Load user information into the page
    loadUserInformation();

    // Setup form event listeners
    setupEventListeners();
});

// Load user information into header and payer section
function loadUserInformation() {
    console.log('=== LOADING USER INFORMATION ===');
    console.log('User object:', currentUser);
    
    // Header information
    const headerUserName = document.getElementById('headerUserName');
    const headerBalance = document.getElementById('headerBalance');
    
    if (headerUserName) {
        headerUserName.textContent = currentUser.full_name;
        console.log('Set header name to:', currentUser.full_name);
    }
    
    if (headerBalance) {
        headerBalance.textContent = formatCurrency(currentUser.available_balance);
        console.log('Set header balance to:', currentUser.available_balance);
    }

    // Payer information section
    const payerName = document.getElementById('payerName');
    const payerPhone = document.getElementById('payerPhone');
    const payerEmail = document.getElementById('payerEmail');
    const payerBalance = document.getElementById('payerBalance');
    
    if (payerName) {
        payerName.textContent = currentUser.full_name;
        console.log('Set payer name to:', currentUser.full_name);
    }
    
    if (payerPhone) {
        payerPhone.textContent = currentUser.phone_number;
        console.log('Set payer phone to:', currentUser.phone_number);
    }
    
    if (payerEmail) {
        payerEmail.textContent = currentUser.email;
        console.log('Set payer email to:', currentUser.email);
    }
    
    if (payerBalance) {
        payerBalance.textContent = formatCurrency(currentUser.available_balance);
        console.log('Set payer balance to:', currentUser.available_balance);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Student ID input - enable lookup button when valid
    const studentIdInput = document.getElementById('studentId');
    if (studentIdInput) {
        studentIdInput.addEventListener('input', function () {
            const lookupBtn = document.querySelector('.lookup-btn');
            if (lookupBtn) {
                lookupBtn.disabled = this.value.trim().length < 7;
            }
        });
    }

    // Prevent form submission and handle button click directly
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent form submission
        });
    }

    // Attach click handler to confirm button
    const confirmBtn = document.getElementById('confirmBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent any default action
            handlePaymentConfirmation();
        });
    }

    // OTP input - auto-format
    const otpInput = document.getElementById('otpCode');
    if (otpInput) {
        otpInput.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }

    
}

// Lookup student by ID using FastAPI
async function lookupStudent() {
    console.log('=== LOOKUP STUDENT CALLED ===');
    
    const studentIdInput = document.getElementById('studentId');
    if (!studentIdInput) {
        console.error('Student ID input not found!');
        return;
    }
    
    const studentId = studentIdInput.value.trim().toUpperCase();
    console.log('Looking up student ID:', studentId);

    if (!studentId || studentId.length < 7) {
        showMessage('Please enter a valid student ID', 'error');
        return;
    }

    const lookupBtn = document.querySelector('.lookup-btn');
    const originalText = lookupBtn ? lookupBtn.textContent : 'Lookup';

    try {
        // Show loading state
        if (lookupBtn) {
            lookupBtn.disabled = true;
            lookupBtn.innerHTML = '<span class="loading-spinner"></span>Looking up...';
        }

        console.log('Fetching student information...');

        // Fetch student information directly (no pending transaction check here)
        const response = await fetch(
            `${API_BASE_URL}/customers/receiver/${studentId}`,
            {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        console.log('Student response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Student data received:', data);
            
            // Check if student has unpaid tuition debt
            if (!data.Debt || !data.Debt.debt_id || !data.Debt.amount || data.Debt.amount <= 0 || data.Debt.status === 'PAID') {
                console.log('No unpaid tuition debt found for this student');
                showMessage('This student has no pending tuition debt. All tuition fees have been paid.', 'info');
                hideStudentInformation();
                const confirmBtn = document.getElementById('confirmBtn');
                if (confirmBtn) confirmBtn.disabled = true;
                return;
            }
            
            // Transform the data to match frontend expectations
            currentStudent = {
                student_id: data.Customer.student_id,
                full_name: data.Customer.full_name,
                program: data.Customer.program,
                tuition: {
                    debt_id: data.Debt.debt_id,
                    amount: data.Debt.amount,
                    semester: data.Debt.semester,
                    academic_year: data.Debt.academic_year,
                    due_date: data.Debt.due_date,
                    status: data.Debt.status
                }
            };

            console.log('Transformed student data:', currentStudent);
            displayStudentInformation(currentStudent);
            showMessage('Student information retrieved successfully!', 'success');

            // Enable confirm button
            const confirmBtn = document.getElementById('confirmBtn');
            if (confirmBtn) {
                confirmBtn.disabled = false;
                console.log('Confirm button enabled');
            }
        } else {
            const errorData = await response.json();
            console.error('Error fetching student:', errorData);
            showMessage(errorData.detail || 'Student not found or no pending tuition debt', 'error');
            hideStudentInformation();
            const confirmBtn = document.getElementById('confirmBtn');
            if (confirmBtn) confirmBtn.disabled = true;
        }

    } catch (error) {
        console.error('Lookup error:', error);
        showMessage('Failed to retrieve student information. Please check if the backend is running.', 'error');
        hideStudentInformation();
        const confirmBtn = document.getElementById('confirmBtn');
        if (confirmBtn) confirmBtn.disabled = true;
    } finally {
        // Restore button
        if (lookupBtn) {
            lookupBtn.disabled = false;
            lookupBtn.innerHTML = originalText;
        }
    }
}

// Display student information
function displayStudentInformation(student) {
    console.log('=== DISPLAYING STUDENT INFORMATION ===');
    console.log('Student:', student);
    
    const elements = {
        studentName: document.getElementById('studentName'),
        studentProgram: document.getElementById('studentProgram'),
        tuitionAmount: document.getElementById('tuitionAmount'),
        semester: document.getElementById('semester'),
        academicYear: document.getElementById('academicYear'),
        dueDate: document.getElementById('dueDate'),
        studentDetails: document.getElementById('studentDetails')
    };

    if (elements.studentName) elements.studentName.textContent = student.full_name;
    if (elements.studentProgram) elements.studentProgram.textContent = student.program;
    if (elements.tuitionAmount) elements.tuitionAmount.textContent = formatCurrency(student.tuition.amount);
    if (elements.semester) elements.semester.textContent = student.tuition.semester;
    if (elements.academicYear) elements.academicYear.textContent = student.tuition.academic_year;
    if (elements.dueDate) elements.dueDate.textContent = formatDate(student.tuition.due_date);

    // Show the student details section
    if (elements.studentDetails) {
        elements.studentDetails.style.display = 'block';
        console.log('Student details section shown');
    }
}

// Hide student information
function hideStudentInformation() {
    const studentDetails = document.getElementById('studentDetails');
    if (studentDetails) {
        studentDetails.style.display = 'none';
    }
    currentStudent = null;
}

// Handle payment confirmation
async function handlePaymentConfirmation() {
    console.log('=== PAYMENT CONFIRMATION ===');
    
    // Validate that student information is loaded
    if (!currentStudent) {
        showMessage('Please lookup student information first', 'error');
        return;
    }

    // Validate that student has unpaid debt
    if (!currentStudent.tuition.debt_id || !currentStudent.tuition.amount || currentStudent.tuition.amount <= 0) {
        showMessage('Cannot process payment: No valid tuition debt found', 'error');
        return;
    }

    // Validate balance
    const tuitionAmount = currentStudent.tuition.amount;
    const availableBalance = currentUser.available_balance;

    console.log('Tuition amount:', tuitionAmount);
    console.log('Available balance:', availableBalance);

    if (tuitionAmount > availableBalance) {
        showMessage('Insufficient balance. Please top up your account.', 'error');
        return;
    }

    try {
        // Check for pending transactions before proceeding
        console.log('Checking for pending transactions...');
        
        const checkResponse = await fetch(
            `${API_BASE_URL}/customers/receiver/check/${currentStudent.student_id}`,
            {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        console.log('Check response status:', checkResponse.status);

        if (checkResponse.ok) {
            const checkData = await checkResponse.json();
            console.log('Check data:', checkData);
            
            if (checkData.result === true) {
                showMessage('There is already a pending transaction for this student. Please try again later.', 'error');
                return;
            }
        }

        // If no pending transactions, proceed to OTP modal
        openOtpModal();

        await processPayment()
    } catch (error) {
        console.error('Error checking pending transactions:', error);
        showMessage('Failed to verify transaction status. Please try again.', 'error');
    }
}

// Open OTP Modal
function openOtpModal() {
    const modal = document.getElementById('otpModal');
    const otpEmailSpan = document.getElementById('otpEmail');
    const otpInput = document.getElementById('otpCode');
    const otpError = document.getElementById('otpError');

    if (otpEmailSpan) otpEmailSpan.textContent = currentUser.email;
    if (otpInput) otpInput.value = '';
    if (otpError) otpError.style.display = 'none';
    if (modal) modal.style.display = 'block';

    // Start OTP timer (5 minutes)
    startOtpTimer(300);

    console.log('OTP modal opened - In production, OTP would be sent to:', currentUser.email);
}

// Close OTP Modal
function closeOtpModal() {
    const modal = document.getElementById('otpModal');
    if (modal) modal.style.display = 'none';

    // Clear timer
    if (otpTimerInterval) {
        clearInterval(otpTimerInterval);
    }
}

// Start OTP timer
function startOtpTimer(seconds) {
    if (otpTimerInterval) {
        clearInterval(otpTimerInterval);
    }

    let timeRemaining = seconds;
    const timerDisplay = document.getElementById('otpTimer');

    otpTimerInterval = setInterval(function () {
        const minutes = Math.floor(timeRemaining / 60);
        const secs = timeRemaining % 60;

        if (timerDisplay) {
            timerDisplay.textContent = `${minutes}:${secs.toString().padStart(2, '0')}`;
        }

        if (timeRemaining <= 0) {
            clearInterval(otpTimerInterval);
            if (timerDisplay) timerDisplay.textContent = 'EXPIRED';
            showOtpError('OTP has expired. Please request a new one.');
        }

        timeRemaining--;
    }, 1000);
}

// Verify OTP and complete payment
async function verifyOtp() {
    const otpInput = document.getElementById('otpCode');
    const otpCode = otpInput ? otpInput.value.trim() : '';

    if (!otpCode || otpCode.length !== 6) {
        showOtpError('Please enter a valid 6-digit OTP code');
        return;
    }

    const otpError = document.getElementById('otpError');
    if (otpError) otpError.style.display = 'none';

    try {
        console.log('Verifying OTP:', otpCode);
        
        if (otpCode.length === 6 && /^\d+$/.test(otpCode)) {
            
            // await processPayment();

            const verifyOtpData = {
                transaction_id : transaction_id,
                otp : otpCode
            };

            console.log('Request Body for OTP', JSON.stringify(verifyOtpData))

            const response = await fetch(`${API_BASE_URL}/otp/verify`, {
                method: 'POST',
                headers: {
                    'Authorization' : `Bearer ${accessToken}`,
                    'Content-Type' : 'application/json'
                },
                body: JSON.stringify(verifyOtpData)
            });

            console.log('Verify OTP status:', response.status)

            if(response.ok){
                // show completion screen
                showSuccessPage(transaction_id)
                transaction_id = null

                closeOtpModal();
            }else{
                showOtpError('Invalid OTP code')
            }
        } else {
            showOtpError('Invalid OTP code');
        }
    } catch (error) {
        console.error('OTP verification error:', error);
        showOtpError('Verification failed. Please try again.');
    }
}

// Process payment using FastAPI
async function processPayment() {
    try {
        showMessage('Processing payment...', 'info');
        console.log('=== PROCESSING PAYMENT ===');

        const transactionData = {
            payer_id: currentUser.customer_id,
            receiver_id: currentStudent.student_id,
            debt_id: currentStudent.tuition.debt_id,
            amount: currentStudent.tuition.amount,
            available_balance: currentUser.available_balance
        };

        console.log('Transaction data:', transactionData);

        const response = await fetch(`${API_BASE_URL}/transactions/create`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transactionData)
        });

        console.log('Payment response status:', response.status);

        if (response.ok) {
            const result = await response.json();
            console.log('Transaction created:', result);
            
            // Update user balance locally
            currentUser.available_balance -= currentStudent.tuition.amount;
            sessionStorage.setItem('user', JSON.stringify(currentUser));

            transaction_id = result.transaction_id
            // showSuccessPage(result.transaction_id);
        } else {
            const errorData = await response.json();
            console.error('Payment failed:', errorData);
            showMessage(errorData.detail || 'Payment failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Payment error:', error);
        showMessage('Payment processing failed. Please check your connection and try again.', 'error');
    }
}

// Show success page
function showSuccessPage(transactionId) {
    const successHtml = `
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                    background: rgba(0, 0, 0, 0.8); z-index: 3000; 
                    display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 50px; border-radius: 20px; 
                        text-align: center; max-width: 500px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
                <div style="font-size: 60px; color: #48bb78; margin-bottom: 20px;">✓</div>
                <h2 style="font-size: 28px; color: #2d3748; margin-bottom: 15px;">Payment Successful!</h2>
                <p style="font-size: 16px; color: #718096; margin-bottom: 20px;">
                    Tuition payment of <strong>${formatCurrency(currentStudent.tuition.amount)}</strong>
                    for student <strong>${currentStudent.full_name}</strong> has been completed successfully.
                </p>
                ${transactionId ? `<p style="font-size: 13px; color: #a0aec0; margin-bottom: 20px; font-family: 'Courier New', monospace;">
                    Transaction ID: ${transactionId}
                </p>` : ''}
                <p style="font-size: 14px; color: #718096; margin-bottom: 30px;">
                    A confirmation email has been sent to <strong>${currentUser.email}</strong>
                </p>
                <button onclick="returnToPaymentPage()" 
                        style="padding: 15px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                               color: white; border: none; border-radius: 12px; font-size: 16px; 
                               font-weight: 600; cursor: pointer;">
                    Make Another Payment
                </button>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', successHtml);
}

// Return to payment page
function returnToPaymentPage() {
    location.reload();
}

// Reset form
function resetForm() {
    const studentIdInput = document.getElementById('studentId');
    if (studentIdInput) studentIdInput.value = '';

    hideStudentInformation();

    const confirmBtn = document.getElementById('confirmBtn');
    if (confirmBtn) confirmBtn.disabled = true;

    const messageBox = document.getElementById('messageBox');
    if (messageBox) messageBox.style.display = 'none';

    currentStudent = null;
}

// Show message
function showMessage(message, type = 'info') {
    const messageBox = document.getElementById('messageBox');
    if (messageBox) {
        messageBox.textContent = message;
        messageBox.className = `message-box ${type}`;
        messageBox.style.display = 'block';

        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 5000);
    }
}

// Show OTP error
function showOtpError(message) {
    const otpError = document.getElementById('otpError');
    if (otpError) {
        otpError.textContent = message;
        otpError.style.display = 'block';
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// resend otp function
function resendOtp() {
    console.log('Clicked otp resend button')
    if(transaction_id != null) {
        const response = fetch(`${API_BASE_URL}/otp/resend/${transaction_id}`,
        {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        })

        if(response.ok) {
            showOtpError('A new otp has been sent to your email')
        }
    }
}

// Logout function
function logout() {
    console.log('Logging out...');
    sessionStorage.clear();
    window.location.href = './login.html';
}

// Close modal when clicking outside
// window.onclick = function (event) {
//     const modal = document.getElementById('otpModal');
//     if (event.target === modal) {
//         closeOtpModal();
//     }
// };