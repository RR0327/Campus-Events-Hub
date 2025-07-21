// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Tab Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all nav items and tab contents
            navItems.forEach(nav => nav.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Add active class to clicked nav item
            this.classList.add('active');
            
            // Show corresponding tab content
            const targetTab = this.getAttribute('data-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // Event Filter
    const filterBtns = document.querySelectorAll('.filter-btn');
    const eventCards = document.querySelectorAll('.event-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all filter buttons
            filterBtns.forEach(filter => filter.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            const filterValue = this.getAttribute('data-filter');
            
            // Show/hide event cards based on filter
            eventCards.forEach(card => {
                if (filterValue === 'all') {
                    card.style.display = 'block';
                } else {
                    const cardStatus = card.getAttribute('data-status');
                    if (cardStatus === filterValue) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        });
    });

    // Save Settings
    const saveBtn = document.querySelector('.save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            // Get form values
            const name = document.getElementById('settingsName').value;
            const email = document.getElementById('settingsEmail').value;
            const department = document.getElementById('settingsDepartment').value;
            
            // Update profile information in sidebar
            document.getElementById('studentName').textContent = name;
            document.getElementById('welcomeName').textContent = name.split(' ')[0];
            document.getElementById('department').textContent = department + ' Department';
            
            // Show success message
            showNotification('Settings saved successfully!', 'success');
        });
    }

    // Notification function
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Add CSS for notification animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);

    // Load user data (simulated)
    loadUserData();

    function loadUserData() {
        // Simulate loading user data from localStorage or API
        const userData = {
            name: 'John Doe',
            studentId: '190104001',
            department: 'CSE',
            email: 'john.doe@student.baiust.edu.bd',
            totalEvents: 12,
            totalAchievements: 5,
            totalClubs: 3,
            totalPoints: 284
        };

        // Update UI with user data
        if (document.getElementById('studentName')) {
            document.getElementById('studentName').textContent = userData.name;
            document.getElementById('welcomeName').textContent = userData.name.split(' ')[0];
            document.getElementById('studentId').textContent = `ID: ${userData.studentId}`;
            document.getElementById('department').textContent = `${userData.department} Department`;
            document.getElementById('totalEvents').textContent = userData.totalEvents;
            document.getElementById('totalAchievements').textContent = userData.totalAchievements;
            document.getElementById('totalClubs').textContent = userData.totalClubs;
            document.getElementById('totalPoints').textContent = userData.totalPoints;
            
            // Update settings form
            if (document.getElementById('settingsName')) {
                document.getElementById('settingsName').value = userData.name;
                document.getElementById('settingsEmail').value = userData.email;
                document.getElementById('settingsDepartment').value = userData.department;
            }
        }
    }

    // Achievement card hover effects
    const achievementCards = document.querySelectorAll('.achievement-card');
    achievementCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Activity item animations
    const activityItems = document.querySelectorAll('.activity-item');
    activityItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
        item.classList.add('fade-in');
    });

    // Add fade-in animation CSS
    const animationStyle = document.createElement('style');
    animationStyle.textContent = `
        .fade-in {
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            transform: translateY(20px);
        }
        
        @keyframes fadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(animationStyle);
});