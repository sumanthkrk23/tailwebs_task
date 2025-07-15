// main.js

// Toast utility
function showToast(message) {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'fixed top-6 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 text-lg transition-opacity duration-300 opacity-0';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.remove('opacity-0');
    toast.classList.add('opacity-100');
    setTimeout(() => {
        toast.classList.remove('opacity-100');
        toast.classList.add('opacity-0');
    }, 500);
}

// --- LOGIN PAGE LOGIC ---
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const res = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (res.ok && data.token) {
            localStorage.setItem('jwt', data.token);
            document.cookie = "jwt=" + data.token + "; path=/";
            showToast('Login successful!');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 300);
        } else {
            document.getElementById('loginError').textContent = data.message || 'Login failed';
            document.getElementById('loginError').classList.remove('hidden');
        }
    });
}

// --- DASHBOARD PAGE LOGIC ---
async function fetchStudents() {
    const token = localStorage.getItem('jwt');
    const res = await fetch('/students', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    if (res.status === 401) {
        window.location.href = '/login';
        return;
    }
    const students = await res.json();
    const tbody = document.getElementById('studentTableBody');
    tbody.innerHTML = '';
    students.forEach(student => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-red-50 transition';
        tr.innerHTML = `
            <td class="py-3 px-4">${student.name}</td>
            <td class="py-3 px-4">${student.subject}</td>
            <td class="py-3 px-4">${student.mark}</td>
            <td class="py-3 px-4">
                <button class="editBtn text-blue-500 mr-2" data-id="${student.id}">Edit</button>
                <button class="deleteBtn text-red-500" data-id="${student.id}">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

if (document.getElementById('studentTableBody')) {
    fetchStudents();
}

// Modal logic
const studentModal = document.getElementById('studentModal');
const addStudentBtn = document.getElementById('addStudentBtn');
const cancelModalBtn = document.getElementById('cancelModalBtn');
const studentForm = document.getElementById('studentForm');
let editStudentId = null;

if (addStudentBtn) {
    addStudentBtn.onclick = () => {
        editStudentId = null;
        document.getElementById('modalTitle').textContent = 'Add Student';
        studentForm.reset();
        studentModal.classList.remove('hidden');
    };
}
if (cancelModalBtn) {
    cancelModalBtn.onclick = () => {
        studentModal.classList.add('hidden');
    };
}
if (studentForm) {
    studentForm.onsubmit = async (e) => {
        e.preventDefault();
        const name = document.getElementById('studentName').value;
        const subject = document.getElementById('studentSubject').value;
        const mark = document.getElementById('studentMark').value;
        const token = localStorage.getItem('jwt');
        let url = '/students';
        let method = 'POST';
        if (editStudentId) {
            url = `/students/${editStudentId}`;
            method = 'PUT';
        }
        const res = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ name, subject, mark })
        });
        if (res.ok) {
            studentModal.classList.add('hidden');
            fetchStudents();
        }
    };
}

// Edit/Delete button logic
if (document.getElementById('studentTableBody')) {
    document.getElementById('studentTableBody').onclick = async (e) => {
        if (e.target.classList.contains('editBtn')) {
            editStudentId = e.target.dataset.id;
            const row = e.target.closest('tr');
            document.getElementById('studentName').value = row.children[0].textContent;
            document.getElementById('studentSubject').value = row.children[1].textContent;
            document.getElementById('studentMark').value = row.children[2].textContent;
            document.getElementById('modalTitle').textContent = 'Edit Student';
            studentModal.classList.remove('hidden');
        } else if (e.target.classList.contains('deleteBtn')) {
            const id = e.target.dataset.id;
            const token = localStorage.getItem('jwt');
            if (confirm('Are you sure you want to delete this student?')) {
                await fetch(`/students/${id}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                fetchStudents();
            }
        }
    };
}

// Logout
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.onclick = () => {
        localStorage.removeItem('jwt');
        document.cookie = 'jwt=; Max-Age=0; path=/';
        showToast('Logout successful!');
        setTimeout(() => {
            window.location.href = '/login';
        }, 300);
    };
} 