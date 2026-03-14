// Dynamic add row for receipt/delivery formsets
document.addEventListener('DOMContentLoaded', function () {
  const addBtn = document.getElementById('add-row');
  const tbody = document.getElementById('formset-body');
  const totalForms = document.querySelector('[name$="-TOTAL_FORMS"]');

  if (addBtn && tbody && totalForms) {
    addBtn.addEventListener('click', function () {
      const rows = tbody.querySelectorAll('.formset-row');
      const formCount = rows.length;
      const lastRow = rows[rows.length - 1];
      const newRow = lastRow.cloneNode(true);

      // Update all input/select names and ids
      newRow.querySelectorAll('input, select').forEach(function (el) {
        if (el.name) {
          el.name = el.name.replace(/-\d+-/, '-' + formCount + '-');
        }
        if (el.id) {
          el.id = el.id.replace(/-\d+-/, '-' + formCount + '-');
        }
        if (el.type === 'checkbox' || el.type === 'radio') {
          el.checked = false;
        } else {
          el.value = '';
        }
      });

      tbody.appendChild(newRow);
      totalForms.value = formCount + 1;
    });
  }

  // Global search in topbar: redirect to products listing with query
  const globalSearch = document.getElementById('globalSearch');
  if (globalSearch) {
    globalSearch.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        const q = globalSearch.value.trim();
        const baseUrl = '/products/';
        const url = q ? baseUrl + '?q=' + encodeURIComponent(q) : baseUrl;
        window.location.href = url;
      }
    });
  }
});