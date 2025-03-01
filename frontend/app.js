document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const statusSection = document.getElementById('status-section');
    const statusMessage = document.getElementById('status-message');
    const progressBar = document.getElementById('progress-bar');
    const downloadBtn = document.getElementById('download-btn');
    
    let jobId = null;
    let pollInterval = null;
    
    // Handle form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(uploadForm);
        
        // Show status section
        statusSection.classList.remove('hidden');
        statusMessage.textContent = 'Uploading files...';
        progressBar.style.width = '10%';
        
        try {
            // Send files to backend
            const response = await fetch('/api/upload/', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }
            
            const data = await response.json();
            jobId = data.job_id;
            
            // Update status
            statusMessage.textContent = data.message;
            progressBar.style.width = '30%';
            
            // Begin polling for results
            pollForResults();
            
        } catch (error) {
            statusMessage.textContent = `Error: ${error.message}`;
            progressBar.style.width = '0%';
            progressBar.classList.add('error');
        }
    });
    
    // Poll for processing results
    function pollForResults() {
        if (pollInterval) {
            clearInterval(pollInterval);
        }
        
        progressBar.style.width = '50%';
        
        pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/results/${jobId}`);
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json')) {
                    // Still processing
                    const data = await response.json();
                    statusMessage.textContent = data.message;
                    progressBar.style.width = '70%';
                } else if (contentType && contentType.includes('application/pdf')) {
                    // Processing complete, PDF available
                    clearInterval(pollInterval);
                    statusMessage.textContent = 'Processing complete! You can now download the feedback.';
                    progressBar.style.width = '100%';
                    downloadBtn.classList.remove('hidden');
                    downloadBtn.addEventListener('click', () => {
                        window.location.href = `/api/results/${jobId}`;
                    });
                }
            } catch (error) {
                statusMessage.textContent = `Error checking status: ${error.message}`;
                clearInterval(pollInterval);
            }
        }, 3000); // Check every 3 seconds
    }
    
    // Reset form when needed
    const resetForm = () => {
        uploadForm.reset();
        statusSection.classList.add('hidden');
        progressBar.style.width = '0%';
        progressBar.classList.remove('error');
        downloadBtn.classList.add('hidden');
        if (pollInterval) {
            clearInterval(pollInterval);
        }
    };
}); 