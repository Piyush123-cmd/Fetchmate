function fetchFormats() {
  const url = document.getElementById('urlInput').value.trim();
  const spinner = document.getElementById('spinner');
  const select = document.getElementById('formatSelect');
  const formatSection = document.getElementById('format-section');
  const formUrl = document.getElementById('formUrl');

  if (!url) {
    alert('Please enter a YouTube video URL.');
    return;
  }

  // Show spinner
  spinner.style.display = 'block';
  formatSection.style.display = 'none';
  select.innerHTML = '<option value="">Select Quality</option>';

  // Send POST to get_formats
  const formData = new FormData();
  formData.append('url', url);

  fetch('/get_formats', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    spinner.style.display = 'none';

    if (data.error) {
      alert("Error fetching formats: " + data.error);
      return;
    }

    if (data.formats.length === 0) {
      alert("No formats available.");
      return;
    }

    // Add options
    data.formats.forEach(f => {
      const option = document.createElement('option');
      option.value = f.format_id;
      option.textContent = f.label;
      select.appendChild(option);
    });

    // Show format section and set hidden input
    formUrl.value = url;
    formatSection.style.display = 'block';
  })
  .catch(err => {
    spinner.style.display = 'none';
    alert("Failed to fetch formats: " + err.message);
  });
}