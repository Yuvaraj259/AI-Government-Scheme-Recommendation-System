document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scheme-form');
    const resultsSection = document.getElementById('results-section');
    const loading = document.getElementById('loading');
    const noResults = document.getElementById('no-results');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Gather Data
        const formData = new FormData(form);
        const data = {
            age: formData.get('age'),
            gender: formData.get('gender'),
            income: formData.get('income'),
            category: formData.get('category'),
            state: formData.get('state'),
            occupation: formData.get('occupation'),
            education: formData.get('education'),
            disability: formData.get('disability')
        };

        // 2. UI Updates
        resultsSection.style.display = 'none';
        loading.style.display = 'block';
        noResults.style.display = 'none';
        resultsSection.innerHTML = '';

        try {
            // 3. API Call
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();

            // 4. Render Results
            loading.style.display = 'none';

            if (result.count > 0) {
                resultsSection.style.display = 'grid'; // Grid layout for cards
                result.schemes.forEach(scheme => {
                    const card = document.createElement('div');
                    card.className = 'scheme-card glass-card'; // Added glass-card
                    card.style.animation = 'fadeInUp 0.5s ease-out'; // Animation

                    const stateBadge = scheme.state
                        ? `<span class="badge badge-state">${scheme.state} Only</span>`
                        : `<span class="badge badge-central">Central Scheme</span>`;

                    card.innerHTML = `
                        <div class="scheme-header">
                            <h3>${scheme.name}</h3>
                        </div>
                        <div style="margin-bottom: 10px;">
                            ${stateBadge}
                        </div>
                        <p class="desc">${scheme.description}</p>
                        
                        <div class="scheme-meta">
                            <span><strong>Benefits:</strong> ${scheme.benefits}</span>
                        </div>

                        <a href="${scheme.application_link}" target="_blank" class="btn-apply">View & Apply →</a>
                    `;
                    resultsSection.appendChild(card);
                });
            } else {
                noResults.style.display = 'block';
            }

        } catch (error) {
            console.error('Error:', error);
            loading.style.display = 'none';
            noResults.innerHTML = '<p style="color:red; text-align:center;">An error occurred while fetching schemes. Please try again.</p>';
            noResults.style.display = 'block';
        }
    });
});
