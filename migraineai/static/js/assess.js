let currentStep = 1;

function goStep(n) {
  document.getElementById(`step${currentStep}`).classList.remove('active');
  document.getElementById(`step${n}`).classList.add('active');
  document.querySelectorAll('.step-tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`[data-step="${n}"]`).classList.add('active');
  document.getElementById('progress').style.width = (n / 3 * 100) + '%';
  currentStep = n;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('.step-tab').forEach(tab => {
  tab.addEventListener('click', () => goStep(parseInt(tab.dataset.step)));
});

function getFormData() {
  const form = document.getElementById('assessForm');
  const data = {};
  form.querySelectorAll('input[type="number"], input[type="text"], select').forEach(el => {
    if (el.name) data[el.name] = el.value;
  });
  form.querySelectorAll('input[type="range"]').forEach(el => {
    if (el.name) data[el.name] = el.value;
  });
  ['nausea','vomit','phonophobia','photophobia','visual','sensory',
   'dysphasia','dysarthria','vertigo','tinnitus','hypoacusis',
   'diplopia','defect','ataxia','conscience','paresthesia'].forEach(name => {
    const el = form.querySelector(`input[name="${name}"]`);
    data[name] = (el && el.checked) ? 1 : 0;
  });
  return data;
}

function validateStep(n) {
  if (n === 1) {
    for (const name of ['age','frequency','duration','location','character','intensity']) {
      const el = document.querySelector(`[name="${name}"]`);
      if (!el || !el.value) {
        el.focus();
        el.style.borderColor = '#f76a6a';
        setTimeout(() => el.style.borderColor = '', 2000);
        return false;
      }
    }
  }
  return true;
}

const _goStep = goStep;
window.goStep = function(n) {
  if (n > currentStep && !validateStep(currentStep)) return;
  _goStep(n);
};

async function submitForm() {
  if (!validateStep(currentStep)) return;
  document.getElementById('assessForm').style.display = 'none';
  document.getElementById('loadingState').style.display = 'block';
  try {
    const res  = await fetch('/api/assess', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(getFormData())
    });
    const data = await res.json();
    if (data.assessment_id) {
      window.location.href = `/result/${data.assessment_id}`;
    } else {
      alert('Something went wrong. Please try again.');
      document.getElementById('assessForm').style.display = 'block';
      document.getElementById('loadingState').style.display = 'none';
    }
  } catch (err) {
    alert('Server error. Make sure Flask is running.');
    document.getElementById('assessForm').style.display = 'block';
    document.getElementById('loadingState').style.display = 'none';
  }
}