document.addEventListener('DOMContentLoaded', () => {
    // 1. Tab Navigation Logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // 2. Fetch Form Configuration
    const formGrid = document.getElementById('form-grid');
    const submitBtn = document.getElementById('calc-btn');
    const spinner = document.getElementById('form-spinner');
    
    // Replace underscores with spaces for readability
    const formatLabel = (str) => {
        return str.replace(/_/g, ' ');
    };

    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';
            const variables = data.variables;
            const optionsMap = data.options;

            variables.forEach(v => {
                const group = document.createElement('div');
                group.className = 'input-group';
                
                const label = document.createElement('label');
                label.textContent = formatLabel(v);
                
                const select = document.createElement('select');
                select.name = v;
                select.required = true;
                
                // default placeholder
                const placeholder = document.createElement('option');
                placeholder.value = "";
                placeholder.textContent = "Select...";
                placeholder.disabled = true;
                placeholder.selected = true;
                select.appendChild(placeholder);
                
                const optArray = optionsMap[v];
                if (optArray) {
                    optArray.forEach(opt => {
                        const optionEl = document.createElement('option');
                        optionEl.value = opt;
                        optionEl.textContent = opt;
                        select.appendChild(optionEl);
                    });
                }
                
                group.appendChild(label);
                group.appendChild(select);
                formGrid.appendChild(group);
            });
            // Bring the button into view inside the grid layout
            formGrid.appendChild(submitBtn);
            submitBtn.style.display = 'block';
        })
        .catch(err => {
            console.error(err);
            spinner.style.display = 'none';
            formGrid.innerHTML = '<p class="muted">Failed to load model config. Ensure `final_scorecard.csv` exists.</p>';
        });

    // 3. Handle Form Submission
    const form = document.getElementById('score-form');
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Disable button during calculation
        submitBtn.textContent = 'Calculating...';
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';

        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());
        
        fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            animateScoreUpdate(data.total_score);
            updateBreakdown(data.breakdown);
        })
        .catch(err => {
            console.error('API Error:', err);
            alert("Calculation failed. Check console.");
        })
        .finally(() => {
            submitBtn.textContent = 'Evaluate Profile ✨';
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
        });
    });

    // Score Ring Animation
    const scoreText = document.getElementById('total-score');
    const scoreRing = document.querySelector('.score-ring');

    function animateScoreUpdate(targetScore) {
        let currentScore = parseInt(scoreText.textContent) || 0;
        if(isNaN(currentScore)) currentScore = 0;
        
        const duration = 1200; // 1.2s
        const startTime = performance.now();

        // Dynamically style the ring based on score outcome (green vs red)
        if(targetScore > 600) {
            scoreRing.style.borderColor = 'rgba(16, 185, 129, 0.8)'; // green-ish
            scoreRing.style.boxShadow = '0 0 30px rgba(16, 185, 129, 0.3)';
        } else {
            scoreRing.style.borderColor = 'rgba(239, 68, 68, 0.8)'; // red-ish
            scoreRing.style.boxShadow = '0 0 30px rgba(239, 68, 68, 0.3)';
        }

        function updateNumber(timestamp) {
            const elapsed = timestamp - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // easeOutExpo
            const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            
            const renderScore = Math.floor(currentScore + (targetScore - currentScore) * easeProgress);
            scoreText.textContent = renderScore;

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }
        requestAnimationFrame(updateNumber);
    }

    function updateBreakdown(breakdownArray) {
        const bdContainer = document.getElementById('score-breakdown');
        bdContainer.innerHTML = '';
        
        // Sort breakdown by absolute impact (highest impact first)
        const sorted = breakdownArray.sort((a,b) => Math.abs(b.points) - Math.abs(a.points));

        sorted.forEach(item => {
            const el = document.createElement('div');
            el.className = 'breakdown-item';
            
            const isPositive = item.points >= 0;
            const ptsClass = isPositive ? 'pts-positive' : 'pts-negative';
            const ptsFormatted = isPositive ? `+${item.points}` : item.points;

            el.innerHTML = `
                <span>${formatLabel(item.variable)}: <strong style="color:var(--text-main); font-size:0.8rem">${item.value}</strong></span>
                <span class="breakdown-pts ${ptsClass}">${ptsFormatted} pt</span>
            `;
            bdContainer.appendChild(el);
        });
    }
});
