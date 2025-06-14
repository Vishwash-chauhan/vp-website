// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const mobileAuthSection = document.querySelector('.mobile-only-auth');

    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
        
        // Also toggle the mobile auth section visibility
        if (mobileAuthSection) {
            mobileAuthSection.classList.toggle('active');
        }
    });

    // Close mobile menu when clicking on any link in the mobile menu
    document.querySelectorAll('.nav-link, .mobile-auth-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
            
            // Also hide the mobile auth section
            if (mobileAuthSection) {
                mobileAuthSection.classList.remove('active');
            }
        });
    });

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');

    function handleSearch() {
        const query = searchInput.value.trim();
        if (query) {
            // In a real app, this would redirect to search results
            alert(`Searching for: "${query}"`);
            // Simulate search redirect
            // window.location.href = `/search?q=${encodeURIComponent(query)}`;
        }
    }

    searchBtn.addEventListener('click', handleSearch);
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });    // Expert card interactions
    document.querySelectorAll('.expert-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Prevent card click when clicking the book button
            if (e.target.classList.contains('expert-book-btn')) {
                return;
            }
            const expertName = this.querySelector('h3').textContent;
            // In a real app, this would navigate to the expert's profile
            alert(`Viewing profile for ${expertName}`);
        });
    });

    // Expert "Book Now" button functionality
    document.querySelectorAll('.expert-book-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent triggering the card click
            // The link will handle navigation to the expert detail page
            // No need for alert popup since this is a "View Profile" button
        });
    });

    // Category card interactions
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', function() {
            const categoryName = this.querySelector('h3').textContent;
            // In a real app, this would navigate to the category page
            alert(`Browsing ${categoryName} experts`);
        });
    });

    // CTA button interactions
    document.querySelectorAll('.btn-primary').forEach(button => {
        button.addEventListener('click', function() {
            const buttonText = this.textContent.trim();
            if (buttonText.includes('Get started') || buttonText.includes('View all')) {
                // In a real app, these would navigate to appropriate pages
                alert(`Redirecting to: ${buttonText}`);
            }
        });
    });

    // Header scroll effect
    let lastScrollY = window.scrollY;
    const header = document.querySelector('.header');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = '#fff';
            header.style.backdropFilter = 'none';
        }
    });

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.category-card, .expert-card, .testimonial-card, .step').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });    // Stats counter animation
    function animateStats() {
        const stats = document.querySelectorAll('.stat-number');
        
        stats.forEach(stat => {
            const originalText = stat.textContent.trim();
            
            // Special handling for rating (contains decimal)
            if (originalText.includes('.')) {
                // Keep rating static - no animation for decimal values
                // Set the original value back to ensure it displays correctly
                stat.textContent = originalText;
                return;
            }
            
            // Extract numeric value and suffix for animation
            const numericValue = parseInt(originalText.replace(/[^\d]/g, ''));
            const suffix = originalText.replace(/[\d,]/g, '');
            
            if (numericValue && numericValue > 0) {
                let current = 0;
                const increment = numericValue / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= numericValue) {
                        current = numericValue;
                        clearInterval(timer);
                    }
                    
                    if (numericValue >= 1000) {
                        stat.textContent = Math.floor(current / 1000) + 'k' + suffix;
                    } else {
                        stat.textContent = Math.floor(current) + suffix;
                    }
                }, 50);
            }
        });
    }

    // Trigger stats animation when hero section is visible
    const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
                heroObserver.disconnect();
            }
        });
    });

    const heroStats = document.querySelector('.hero-stats');
    if (heroStats) {
        heroObserver.observe(heroStats);
    }    // Form validation (if forms are added)
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Phone number validation
    function validatePhoneNumber(phone) {
        // Remove all non-digit characters
        const cleanPhone = phone.replace(/\D/g, '');
        // Check if it's a valid length (10-15 digits) and format
        const re = /^[\+]?[1-9][\d]{9,14}$/;
        return re.test(phone) || /^[\d\-\+\(\)\s]{10,}$/.test(phone);
    }

    // Newsletter signup (placeholder)
    function handleNewsletterSignup(email) {
        if (validateEmail(email)) {
            alert('Thank you for subscribing to our newsletter!');
            return true;
        } else {
            alert('Please enter a valid email address.');
            return false;
        }
    }

    // Loading states for buttons
    function showLoadingState(button) {
        const originalText = button.textContent;
        button.textContent = 'Loading...';
        button.disabled = true;
        
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 1500);
    }

    // Add loading states to primary buttons
    document.querySelectorAll('.btn-primary').forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                showLoadingState(this);
            }
        });
    });

    // Lazy loading for images
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.opacity = '1';
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img').forEach(img => {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
        img.addEventListener('load', () => {
            img.style.opacity = '1';
        });
        imageObserver.observe(img);
    });

    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // ESC key closes mobile menu
        if (e.key === 'Escape' && navMenu.classList.contains('active')) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        }
    });

    // Focus management for accessibility
    const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    
    function trapFocus(element) {
        const focusableContent = element.querySelectorAll(focusableElements);
        const firstFocusableElement = focusableContent[0];
        const lastFocusableElement = focusableContent[focusableContent.length - 1];

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusableElement) {
                        lastFocusableElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastFocusableElement) {
                        firstFocusableElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }

    // Initialize tooltips (if needed)
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = this.getAttribute('data-tooltip');
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.position = 'absolute';
                tooltip.style.top = rect.top - 30 + 'px';
                tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
                tooltip.style.background = '#333';
                tooltip.style.color = 'white';
                tooltip.style.padding = '5px 10px';
                tooltip.style.borderRadius = '4px';
                tooltip.style.fontSize = '12px';
                tooltip.style.zIndex = '9999';
            });
            
            element.addEventListener('mouseleave', function() {
                const tooltip = document.querySelector('.tooltip');
                if (tooltip) {
                    tooltip.remove();
                }
            });
        });
    }

    // Initialize all functionality
    initTooltips();
    
    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            const loadTime = performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart;
            console.log('Page load time:', loadTime + 'ms');
        });
    }

    console.log('Clarity website replica initialized successfully!');

    // Sign Up Form Validation and Handling
    const signupForm = document.querySelector('.signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = {
                firstName: document.getElementById('firstName').value.trim(),
                lastName: document.getElementById('lastName').value.trim(),
                email: document.getElementById('email').value.trim(),
                password: document.getElementById('password').value,
                confirmPassword: document.getElementById('confirmPassword').value,
                accountType: document.getElementById('accountType').value,
                terms: document.getElementById('terms').checked
            };
            
            // Validation
            if (!validateSignupForm(formData)) {
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('.btn-signup-submit');
            showLoadingState(submitBtn);
            
            // Simulate API call
            setTimeout(() => {
                alert('Account created successfully! Please check your email to verify your account.');
                // In a real app, redirect to dashboard or email verification page
                window.location.href = 'index.html';
            }, 1500);
        });
        
        // Real-time password confirmation validation
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirmPassword');
        
        function validatePasswordMatch() {
            if (confirmPassword.value && password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity('Passwords do not match');
                confirmPassword.style.borderColor = '#dc3545';
            } else {
                confirmPassword.setCustomValidity('');
                confirmPassword.style.borderColor = '#e9ecef';
            }
        }
        
        password.addEventListener('input', validatePasswordMatch);
        confirmPassword.addEventListener('input', validatePasswordMatch);
        
        // Password strength indicator
        password.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            showPasswordStrength(strength);
        });
    }
    
    function validateSignupForm(data) {        // Check required fields
        if (!data.firstName || !data.lastName || !data.contactNumber || !data.email || !data.password || !data.accountType) {
            alert('Please fill in all required fields.');
            return false;
        }
        
        // Validate contact number format
        if (!validatePhoneNumber(data.contactNumber)) {
            alert('Please enter a valid contact number.');
            return false;
        }
        
        // Validate email format
        if (!validateEmail(data.email)) {
            alert('Please enter a valid email address.');
            return false;
        }
        
        // Validate password strength
        if (data.password.length < 8) {
            alert('Password must be at least 8 characters long.');
            return false;
        }
        
        // Check password match
        if (data.password !== data.confirmPassword) {
            alert('Passwords do not match.');
            return false;
        }
        
        // Check terms agreement
        if (!data.terms) {
            alert('Please agree to the Terms of Service and Privacy Policy.');
            return false;
        }
        
        return true;
    }
    
    function checkPasswordStrength(password) {
        let strength = 0;
        const checks = {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
        
        strength = Object.values(checks).filter(Boolean).length;
        
        return {
            score: strength,
            checks: checks,
            level: strength < 3 ? 'weak' : strength < 5 ? 'medium' : 'strong'
        };
    }
    
    function showPasswordStrength(strength) {
        // Remove existing strength indicator
        const existingIndicator = document.querySelector('.password-strength');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        // Create new strength indicator
        const passwordField = document.getElementById('password');
        const indicator = document.createElement('div');
        indicator.className = 'password-strength';
        indicator.style.marginTop = '0.5rem';
        indicator.style.fontSize = '0.875rem';
        
        const colors = {
            weak: '#dc3545',
            medium: '#ffc107',
            strong: '#28a745'
        };
        
        indicator.style.color = colors[strength.level];
        indicator.textContent = `Password strength: ${strength.level}`;
        
        passwordField.parentNode.appendChild(indicator);
    }
});

// Experts Page Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the experts page
    if (window.location.pathname.includes('experts.html') || document.querySelector('.all-experts-grid')) {
        initializeExpertsPage();
    }
});

function initializeExpertsPage() {
    const searchInput = document.getElementById('expertSearch');
    const categoryFilter = document.getElementById('categoryFilter');
    const priceFilter = document.getElementById('priceFilter');
    const ratingFilter = document.getElementById('ratingFilter');
    const clearFiltersBtn = document.querySelector('.clear-filters-btn');
    const resultsCount = document.getElementById('resultsCount');
    const expertCards = document.querySelectorAll('.expert-card');

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterExperts();
        });
    }

    // Filter functionality
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterExperts);
    }
    if (priceFilter) {
        priceFilter.addEventListener('change', filterExperts);
    }
    if (ratingFilter) {
        ratingFilter.addEventListener('change', filterExperts);
    }

    // Clear filters
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            searchInput.value = '';
            categoryFilter.value = '';
            priceFilter.value = '';
            ratingFilter.value = '';
            filterExperts();
        });
    }

    // Search button functionality
    const searchBtn = document.querySelector('.search-btn-experts');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            filterExperts();
        });
    }

    function filterExperts() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const selectedCategory = categoryFilter ? categoryFilter.value : '';
        const selectedPriceRange = priceFilter ? priceFilter.value : '';
        const selectedRating = ratingFilter ? ratingFilter.value : '';

        let visibleCount = 0;

        expertCards.forEach(card => {
            let isVisible = true;

            // Search filter
            if (searchTerm) {
                const expertName = card.querySelector('h3').textContent.toLowerCase();
                const expertTitle = card.querySelector('.expert-title').textContent.toLowerCase();
                const expertDescription = card.querySelector('.expert-description').textContent.toLowerCase();
                
                if (!expertName.includes(searchTerm) && 
                    !expertTitle.includes(searchTerm) && 
                    !expertDescription.includes(searchTerm)) {
                    isVisible = false;
                }
            }

            // Category filter
            if (selectedCategory && isVisible) {
                const cardCategories = card.getAttribute('data-categories');
                if (cardCategories) {
                    const categoryIds = cardCategories.split(',');
                    if (!categoryIds.includes(selectedCategory)) {
                        isVisible = false;
                    }
                } else {
                    isVisible = false;
                }
            }

            // Price filter
            if (selectedPriceRange && isVisible) {
                const cardPrice = parseInt(card.getAttribute('data-price'));
                let priceInRange = false;

                switch (selectedPriceRange) {
                    case '0-100':
                        priceInRange = cardPrice >= 499 && cardPrice <= 1000;
                        break;
                    case '100-200':
                        priceInRange = cardPrice > 1000 && cardPrice <= 2999;
                        break;
                    case '200-300':
                        priceInRange = cardPrice > 2999 && cardPrice <= 5000;
                        break;
                    case '300+':
                        priceInRange = cardPrice > 5000;
                        break;
                }

                if (!priceInRange) {
                    isVisible = false;
                }
            }

            // Rating filter
            if (selectedRating && isVisible) {
                const cardRating = parseInt(card.getAttribute('data-rating'));
                if (cardRating < parseInt(selectedRating)) {
                    isVisible = false;
                }
            }

            // Show or hide the card
            if (isVisible) {
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.classList.add('hidden');
            }
        });

        // Update results count
        if (resultsCount) {
            const expertText = visibleCount === 1 ? 'expert' : 'experts';
            resultsCount.textContent = `${visibleCount} ${expertText} found`;
        }
    }

    // Load more functionality (placeholder)
    const loadMoreBtn = document.querySelector('.load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            // Placeholder for load more functionality
            alert('Load more functionality would be implemented here with pagination or infinite scroll');
        });
    }

    // Expert card click handling for experts page
    expertCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Prevent card click when clicking the book button
            if (e.target.classList.contains('expert-book-btn')) {
                return;
            }
            const expertName = this.querySelector('h3').textContent;
            // In a real app, this would navigate to the expert's detailed profile
            alert(`Viewing detailed profile for ${expertName}`);
        });
    });

    // Book now buttons for experts page
    document.querySelectorAll('.expert-book-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent triggering the card click
            // The link will handle navigation to the expert detail page
            // No need for alert popup since this is a "View Profile" button
        });
    });
}
