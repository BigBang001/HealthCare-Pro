// Global variables
let currentUser = null;
let authToken = null;
let patients = [];
let doctors = [];
let mappings = [];
let genderChart = null;
let ageChart = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkExistingAuth();
});

function initializeApp() {
    // Configure axios defaults
    axios.defaults.baseURL = window.location.origin;
    axios.defaults.headers.common['Content-Type'] = 'application/json';
    
    // Add request interceptor to include auth token
    axios.interceptors.request.use(
        config => {
            if (authToken) {
                config.headers.Authorization = `Bearer ${authToken}`;
            }
            return config;
        },
        error => Promise.reject(error)
    );
    
    // Add response interceptor to handle auth errors
    axios.interceptors.response.use(
        response => response,
        error => {
            if (error.response?.status === 401) {
                logout();
                showAlert('Session expired. Please login again.', 'warning');
            }
            return Promise.reject(error);
        }
    );
}

function setupEventListeners() {
    // Auth forms
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Entity forms
    document.getElementById('patientForm').addEventListener('submit', handlePatientSubmit);
    document.getElementById('doctorForm').addEventListener('submit', handleDoctorSubmit);
    document.getElementById('mappingForm').addEventListener('submit', handleMappingSubmit);
    
    // Tab change listeners
    document.getElementById('mainTabs').addEventListener('click', handleTabChange);
    
    // Modal event listeners
    document.getElementById('patientModal').addEventListener('show.bs.modal', preparePatientModal);
    document.getElementById('doctorModal').addEventListener('show.bs.modal', prepareDoctorModal);
    document.getElementById('mappingModal').addEventListener('show.bs.modal', prepareMappingModal);
}

function checkExistingAuth() {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('currentUser');
    
    if (token && user) {
        // Verify token is still valid with the server
        authToken = token;
        axios.get('/api/auth/me')
            .then(response => {
                currentUser = response.data.user;
                showMainSection();
            })
            .catch(error => {
                // Token is invalid, clear stored data
                localStorage.removeItem('authToken');
                localStorage.removeItem('currentUser');
                authToken = null;
                currentUser = null;
            });
    }
}

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await axios.post('/api/auth/login', { email, password });
        
        authToken = response.data.access_token;
        currentUser = response.data.user;
        
        // Store in localStorage
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        showAlert('Login successful!', 'success');
        showMainSection();
        
    } catch (error) {
        const message = error.response?.data?.message || 'Login failed';
        showAlert(message, 'danger');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await axios.post('/api/auth/register', { name, email, password });
        
        authToken = response.data.access_token;
        currentUser = response.data.user;
        
        // Store in localStorage
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        showAlert('Registration successful!', 'success');
        showMainSection();
        
    } catch (error) {
        const message = error.response?.data?.message || 'Registration failed';
        showAlert(message, 'danger');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    
    // Clear localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    // Reset forms
    document.getElementById('loginForm').reset();
    document.getElementById('registerForm').reset();
    
    // Show auth section
    document.getElementById('authSection').classList.remove('d-none');
    document.getElementById('mainSection').classList.add('d-none');
    document.getElementById('authButtons').classList.add('d-none');
    
    showAlert('Logged out successfully', 'info');
}

function showMainSection() {
    document.getElementById('authSection').classList.add('d-none');
    document.getElementById('mainSection').classList.remove('d-none');
    document.getElementById('authButtons').classList.remove('d-none');
    document.getElementById('userInfo').textContent = `Welcome, ${currentUser.name}`;
    
    // Load initial data
    loadDashboard();
    loadPatients();
    loadDoctors();
    loadMappings();
}

// Tab change handler
function handleTabChange(e) {
    if (e.target.getAttribute('href') === '#dashboard') {
        loadDashboard();
    } else if (e.target.getAttribute('href') === '#patients') {
        loadPatients();
    } else if (e.target.getAttribute('href') === '#doctors') {
        loadDoctors();
    } else if (e.target.getAttribute('href') === '#mappings') {
        loadMappings();
    }
}

// Dashboard functions
async function loadDashboard() {
    await Promise.all([loadPatients(), loadDoctors(), loadMappings()]);
    updateDashboardStats();
    updateCharts();
}

function updateDashboardStats() {
    // Update navbar stats
    document.getElementById('patientsCount').textContent = `${patients.length} Patients`;
    document.getElementById('doctorsCount').textContent = `${doctors.length} Doctors`;
    document.getElementById('mappingsCount').textContent = `${mappings.length} Assignments`;
    
    // Update dashboard cards
    document.getElementById('dashboardPatientsCount').textContent = patients.length;
    document.getElementById('dashboardDoctorsCount').textContent = doctors.length;
    document.getElementById('dashboardMappingsCount').textContent = mappings.length;
    
    // Calculate average age
    const avgAge = patients.length > 0 ? 
        Math.round(patients.reduce((sum, p) => sum + p.age, 0) / patients.length) : 0;
    document.getElementById('dashboardAvgAge').textContent = avgAge;
    
    // Update specializations list
    updateSpecializationsList();
}

function updateCharts() {
    updateGenderChart();
    updateAgeChart();
}

function updateGenderChart() {
    const ctx = document.getElementById('genderChart').getContext('2d');
    
    if (genderChart) {
        genderChart.destroy();
    }
    
    const genderCounts = patients.reduce((acc, patient) => {
        acc[patient.gender] = (acc[patient.gender] || 0) + 1;
        return acc;
    }, {});
    
    const data = {
        labels: Object.keys(genderCounts).map(g => capitalizeFirst(g)),
        datasets: [{
            data: Object.values(genderCounts),
            backgroundColor: ['#0d6efd', '#dc3545', '#ffc107'],
            borderWidth: 2,
            borderColor: '#ffffff'
        }]
    };
    
    genderChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateAgeChart() {
    const ctx = document.getElementById('ageChart').getContext('2d');
    
    if (ageChart) {
        ageChart.destroy();
    }
    
    const ageGroups = {
        '0-18': 0,
        '19-35': 0,
        '36-50': 0,
        '51-65': 0,
        '65+': 0
    };
    
    patients.forEach(patient => {
        const age = patient.age;
        if (age <= 18) ageGroups['0-18']++;
        else if (age <= 35) ageGroups['19-35']++;
        else if (age <= 50) ageGroups['36-50']++;
        else if (age <= 65) ageGroups['51-65']++;
        else ageGroups['65+']++;
    });
    
    const data = {
        labels: Object.keys(ageGroups),
        datasets: [{
            label: 'Number of Patients',
            data: Object.values(ageGroups),
            backgroundColor: '#0d6efd',
            borderColor: '#0a58ca',
            borderWidth: 1
        }]
    };
    
    ageChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function updateSpecializationsList() {
    const specializations = doctors.reduce((acc, doctor) => {
        const spec = doctor.specialization;
        acc[spec] = (acc[spec] || 0) + 1;
        return acc;
    }, {});
    
    const container = document.getElementById('specializationsList');
    
    if (Object.keys(specializations).length === 0) {
        container.innerHTML = '<p class="text-muted">No doctors added yet</p>';
        return;
    }
    
    const html = Object.entries(specializations)
        .sort((a, b) => b[1] - a[1])
        .map(([spec, count]) => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="fw-medium">${escapeHtml(spec)}</span>
                <span class="badge bg-primary">${count} doctor${count > 1 ? 's' : ''}</span>
            </div>
        `).join('');
    
    container.innerHTML = html;
}

// Patient functions
async function loadPatients() {
    try {
        const response = await axios.get('/api/patients');
        patients = response.data.patients;
        renderPatients();
    } catch (error) {
        console.error('Failed to load patients:', error);
        document.getElementById('patientsContainer').innerHTML = 
            '<div class="alert alert-danger">Failed to load patients</div>';
    }
}

function renderPatients() {
    const container = document.getElementById('patientsContainer');
    
    if (patients.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-user-injured fa-3x text-muted mb-3"></i>
                <h5>No Patients Found</h5>
                <p class="text-muted">Click "Add Patient" to create your first patient record.</p>
            </div>
        `;
        return;
    }
    
    const html = patients.map(patient => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col">
                        <h5 class="card-title mb-1">${escapeHtml(patient.name)}</h5>
                        <p class="card-text text-muted mb-1">
                            <i class="fas fa-birthday-cake me-1"></i>${patient.age} years old
                            <span class="mx-2">•</span>
                            <i class="fas fa-venus-mars me-1"></i>${capitalizeFirst(patient.gender)}
                        </p>
                        ${patient.medical_history ? `
                            <p class="card-text small">
                                <i class="fas fa-notes-medical me-1"></i>${escapeHtml(patient.medical_history)}
                            </p>
                        ` : ''}
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-outline-primary btn-sm me-1" onclick="editPatient('${patient.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="deletePatient('${patient.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

async function handlePatientSubmit(e) {
    e.preventDefault();
    
    const patientId = document.getElementById('patientId').value;
    const name = document.getElementById('patientName').value;
    const age = parseInt(document.getElementById('patientAge').value);
    const gender = document.getElementById('patientGender').value;
    const medical_history = document.getElementById('patientHistory').value;
    
    const data = { name, age, gender, medical_history };
    
    try {
        if (patientId) {
            // Update existing patient
            await axios.put(`/api/patients/${patientId}`, data);
            showAlert('Patient updated successfully!', 'success');
        } else {
            // Create new patient
            await axios.post('/api/patients', data);
            showAlert('Patient created successfully!', 'success');
        }
        
        // Close modal and reload data
        bootstrap.Modal.getInstance(document.getElementById('patientModal')).hide();
        loadPatients();
        updateDashboardStats();
        
    } catch (error) {
        const message = error.response?.data?.message || 'Failed to save patient';
        showAlert(message, 'danger');
    }
}

function preparePatientModal() {
    document.getElementById('patientForm').reset();
    document.getElementById('patientId').value = '';
    document.querySelector('#patientModal .modal-title').textContent = 'Add Patient';
}

function editPatient(patientId) {
    const patient = patients.find(p => p.id === patientId);
    if (!patient) return;
    
    document.getElementById('patientId').value = patient.id;
    document.getElementById('patientName').value = patient.name;
    document.getElementById('patientAge').value = patient.age;
    document.getElementById('patientGender').value = patient.gender;
    document.getElementById('patientHistory').value = patient.medical_history || '';
    
    document.querySelector('#patientModal .modal-title').textContent = 'Edit Patient';
    new bootstrap.Modal(document.getElementById('patientModal')).show();
}

async function deletePatient(patientId) {
    if (!confirm('Are you sure you want to delete this patient?')) return;
    
    try {
        await axios.delete(`/api/patients/${patientId}`);
        showAlert('Patient deleted successfully!', 'success');
        loadPatients();
        updateDashboardStats();
        updateCharts();
    } catch (error) {
        const message = error.response?.data?.message || 'Failed to delete patient';
        showAlert(message, 'danger');
    }
}

// Doctor functions
async function loadDoctors() {
    try {
        const response = await axios.get('/api/doctors');
        doctors = response.data.doctors;
        renderDoctors();
    } catch (error) {
        console.error('Failed to load doctors:', error);
        document.getElementById('doctorsContainer').innerHTML = 
            '<div class="alert alert-danger">Failed to load doctors</div>';
    }
}

function renderDoctors() {
    const container = document.getElementById('doctorsContainer');
    
    if (doctors.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-user-md fa-3x text-muted mb-3"></i>
                <h5>No Doctors Found</h5>
                <p class="text-muted">Click "Add Doctor" to create your first doctor record.</p>
            </div>
        `;
        return;
    }
    
    const html = doctors.map(doctor => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col">
                        <h5 class="card-title mb-1">${escapeHtml(doctor.name)}</h5>
                        <p class="card-text text-muted mb-1">
                            <i class="fas fa-stethoscope me-1"></i>${escapeHtml(doctor.specialization)}
                            <span class="mx-2">•</span>
                            <i class="fas fa-clock me-1"></i>${doctor.experience_years} years experience
                        </p>
                        ${doctor.contact_info ? `
                            <p class="card-text small">
                                <i class="fas fa-phone me-1"></i>${escapeHtml(doctor.contact_info)}
                            </p>
                        ` : ''}
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-outline-primary btn-sm me-1" onclick="editDoctor('${doctor.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteDoctor('${doctor.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

async function handleDoctorSubmit(e) {
    e.preventDefault();
    
    const doctorId = document.getElementById('doctorId').value;
    const name = document.getElementById('doctorName').value;
    const specialization = document.getElementById('doctorSpecialization').value;
    const experience_years = parseInt(document.getElementById('doctorExperience').value);
    const contact_info = document.getElementById('doctorContact').value;
    
    const data = { name, specialization, experience_years, contact_info };
    
    try {
        if (doctorId) {
            // Update existing doctor
            await axios.put(`/api/doctors/${doctorId}`, data);
            showAlert('Doctor updated successfully!', 'success');
        } else {
            // Create new doctor
            await axios.post('/api/doctors', data);
            showAlert('Doctor created successfully!', 'success');
        }
        
        // Close modal and reload data
        bootstrap.Modal.getInstance(document.getElementById('doctorModal')).hide();
        loadDoctors();
        
    } catch (error) {
        const message = error.response?.data?.message || 'Failed to save doctor';
        showAlert(message, 'danger');
    }
}

function prepareDoctorModal() {
    document.getElementById('doctorForm').reset();
    document.getElementById('doctorId').value = '';
    document.querySelector('#doctorModal .modal-title').textContent = 'Add Doctor';
}

function editDoctor(doctorId) {
    const doctor = doctors.find(d => d.id === doctorId);
    if (!doctor) return;
    
    document.getElementById('doctorId').value = doctor.id;
    document.getElementById('doctorName').value = doctor.name;
    document.getElementById('doctorSpecialization').value = doctor.specialization;
    document.getElementById('doctorExperience').value = doctor.experience_years;
    document.getElementById('doctorContact').value = doctor.contact_info || '';
    
    document.querySelector('#doctorModal .modal-title').textContent = 'Edit Doctor';
    new bootstrap.Modal(document.getElementById('doctorModal')).show();
}

async function deleteDoctor(doctorId) {
    if (!confirm('Are you sure you want to delete this doctor?')) return;
    
    try {
        await axios.delete(`/api/doctors/${doctorId}`);
        showAlert('Doctor deleted successfully!', 'success');
        loadDoctors();
    } catch (error) {
        const message = error.response?.data?.message || 'Failed to delete doctor';
        showAlert(message, 'danger');
    }
}

// Mapping functions
async function loadMappings() {
    try {
        const response = await axios.get('/api/mappings');
        mappings = response.data.mappings;
        renderMappings();
    } catch (error) {
        console.error('Failed to load mappings:', error);
        document.getElementById('mappingsContainer').innerHTML = 
            '<div class="alert alert-danger">Failed to load mappings</div>';
    }
}

function renderMappings() {
    const container = document.getElementById('mappingsContainer');
    
    if (mappings.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-link fa-3x text-muted mb-3"></i>
                <h5>No Assignments Found</h5>
                <p class="text-muted">Click "Create Assignment" to assign doctors to patients.</p>
            </div>
        `;
        return;
    }
    
    const html = mappings.map(mapping => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col">
                        <h5 class="card-title mb-1">
                            <i class="fas fa-user-injured me-2"></i>${escapeHtml(mapping.patient_name)}
                            <i class="fas fa-arrow-right mx-2"></i>
                            <i class="fas fa-user-md me-2"></i>${escapeHtml(mapping.doctor_name)}
                        </h5>
                        <p class="card-text text-muted small">
                            <i class="fas fa-calendar me-1"></i>Assigned on ${formatDate(mapping.created_at)}
                        </p>
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteMapping('${mapping.id}')">
                            <i class="fas fa-unlink me-1"></i>Remove
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

async function handleMappingSubmit(e) {
    e.preventDefault();
    
    const patient_id = document.getElementById('mappingPatient').value;
    const doctor_id = document.getElementById('mappingDoctor').value;
    
    try {
        await axios.post('/api/mappings', { patient_id, doctor_id });
        showAlert('Assignment created successfully!', 'success');
        
        // Close modal and reload data
        bootstrap.Modal.getInstance(document.getElementById('mappingModal')).hide();
        loadMappings();
        
    } catch (error) {
        const message = error.response?.data?.message || 'Failed to create assignment';
        showAlert(message, 'danger');
    }
}

async function prepareMappingModal() {
    // Load patients and doctors for dropdowns
    try {
        const [patientsResponse, doctorsResponse] = await Promise.all([
            axios.get('/api/patients'),
            axios.get('/api/doctors')
        ]);
        
        const patientSelect = document.getElementById('mappingPatient');
        const doctorSelect = document.getElementById('mappingDoctor');
        
        // Clear existing options
        patientSelect.innerHTML = '<option value="">Select Patient</option>';
        doctorSelect.innerHTML = '<option value="">Select Doctor</option>';
        
        // Populate patients
        patientsResponse.data.patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.id;
            option.textContent = patient.name;
            patientSelect.appendChild(option);
        });
        
        // Populate doctors
        doctorsResponse.data.doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.id;
            option.textContent = `${doctor.name} (${doctor.specialization})`;
            doctorSelect.appendChild(option);
        });
        
    } catch (error) {
        showAlert('Failed to load data for assignment', 'danger');
    }
}

async function deleteMapping(mappingId) {
    if (!confirm('Are you sure you want to remove this assignment?')) return;
    
    try {
        await axios.delete(`/api/mappings/${mappingId}`);
        showAlert('Assignment removed successfully!', 'success');
        loadMappings();
    } catch (error) {
        const message = error.response?.data?.message || 'Failed to remove assignment';
        showAlert(message, 'danger');
    }
}

// Utility functions
function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer');
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}
