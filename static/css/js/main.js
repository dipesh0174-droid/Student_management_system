document.addEventListener('DOMContentLoaded', function() {
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value;
                if (query.length > 1) {
                    fetch(`/search?q=${encodeURIComponent(query)}`)
                        .then(r => r.json())
                        .then(data => {
                            updateStudentsTable(data);
                        })
                        .catch(err => console.log('Search error:', err));
                }
            }, 400);
        });
    }

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = this.querySelectorAll('input[required]');
            let valid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    valid = false;
                } else {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                }
            });
            
            if (!valid) {
                e.preventDefault();
                showNotification('Please fill all required fields!', 'warning');
            }
        });
    });

    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }, 4000);
        });
    }, 1000);
});

function updateStudentsTable(students) {
    const tbody = document.getElementById('studentsTable');
    if (!tbody) return;
    
    tbody.innerHTML = students.map(student => `
        <tr>
            <td><small>${student._id.slice(0,8)}</small></td>
            <td>${student.name}</td>
            <td><strong>${student.roll_no}</strong></td>
            <td>${student.age}</td>
            <td>
                <span class="badge ${
                    student.marks >= 80 ? 'bg-success' : 
                    student.marks >= 60 ? 'bg-warning' : 'bg-danger'
                }">${student.marks}</span>
            </td>
            <td>${student.class}</td>
            <td>${new Date(student.created_at).toLocaleDateString('en-GB')}</td>
            <td>
                <a href="/delete/${student._id}" class="btn btn-danger btn-sm" 
                   onclick="return confirm('Please Confirm Your Action')">
                    <i class="fas fa-trash"></i>
                </a>
            </td>
        </tr>
    `).join('');
}

function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}
