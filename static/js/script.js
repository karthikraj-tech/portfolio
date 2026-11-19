/**
 * script.js
 * Frontend application logic for Karthikraj S Portfolio.
 * Implements dynamic API data fetching, form validation, theme switching,
 * navigation highlighting, and secure textContent rendering (anti-XSS).
 */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize all interactive modules
  initTheme();
  initNavigation();
  initResumeStatus();
  loadSkills();
  loadProjects();
  loadCertifications();
  initContactForm();
  updateFooterYear();
});

/* --------------------------------------------------------------------------
   1. Theme Management (Light / Dark Mode with LocalStorage persistence)
   -------------------------------------------------------------------------- */
function initTheme() {
  const themeToggleBtn = document.getElementById("theme-toggle");
  if (!themeToggleBtn) return;

  // Retrieve saved theme preference or default to dark
  const savedTheme = localStorage.getItem("portfolio_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);

  themeToggleBtn.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    
    document.documentElement.setAttribute("data-theme", nextTheme);
    localStorage.setItem("portfolio_theme", nextTheme);
  });
}

/* --------------------------------------------------------------------------
   2. Navigation Bar: Mobile Toggle & ScrollSpy Active Highlighting
   -------------------------------------------------------------------------- */
function initNavigation() {
  const mobileToggle = document.getElementById("mobile-toggle");
  const navMenu = document.getElementById("nav-menu");
  const navLinks = document.querySelectorAll(".nav-link");

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener("click", () => {
      const isExpanded = mobileToggle.getAttribute("aria-expanded") === "true";
      mobileToggle.setAttribute("aria-expanded", String(!isExpanded));
      navMenu.classList.toggle("open");
    });

    // Close menu when clicking any nav link
    navLinks.forEach(link => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("open");
        mobileToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // ScrollSpy: Highlight active link based on scroll position
  const sections = document.querySelectorAll("section[id]");
  window.addEventListener("scroll", () => {
    const scrollY = window.pageYOffset;

    sections.forEach(current => {
      const sectionHeight = current.offsetHeight;
      const sectionTop = current.offsetTop - 120;
      const sectionId = current.getAttribute("id");
      const matchingLink = document.querySelector(`.nav-menu a[href*="${sectionId}"]`);

      if (matchingLink) {
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
          navLinks.forEach(l => l.classList.remove("active"));
          matchingLink.classList.add("active");
        }
      }
    });
  }, { passive: true });
}

/* --------------------------------------------------------------------------
   3. Resume Availability Check (Honesty Rule)
   -------------------------------------------------------------------------- */
async function initResumeStatus() {
  const resumeBtn = document.getElementById("resume-btn");
  const resumeText = document.getElementById("resume-btn-text");
  if (!resumeBtn || !resumeText) return;

  try {
    const res = await fetch("/api/resume-status");
    const data = await res.json();

    if (data.available && data.filename) {
      resumeBtn.setAttribute("href", `/static/resume/${encodeURIComponent(data.filename)}`);
      resumeBtn.setAttribute("download", data.filename);
      resumeBtn.removeAttribute("aria-disabled");
      resumeBtn.classList.remove("btn-outline");
      resumeBtn.classList.add("btn-secondary");
      resumeText.textContent = "Download Resume";
    } else {
      // Resume file not found on disk: keep button disabled
      resumeBtn.setAttribute("href", "#");
      resumeBtn.setAttribute("aria-disabled", "true");
      resumeBtn.classList.add("btn-outline");
      resumeBtn.classList.remove("btn-secondary");
      resumeText.textContent = "Resume coming soon";
    }
  } catch (err) {
    console.warn("Unable to check resume availability:", err);
    resumeBtn.setAttribute("href", "#");
    resumeBtn.setAttribute("aria-disabled", "true");
    resumeText.textContent = "Resume coming soon";
  }
}

/* --------------------------------------------------------------------------
   4. Dynamic Skills Loading (GET /api/skills)
   -------------------------------------------------------------------------- */
async function loadSkills() {
  const container = document.getElementById("skills-container");
  if (!container) return;

  try {
    const response = await fetch("/api/skills");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();

    if (!result.data || result.data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No skills recorded in database yet.</p>
        </div>`;
      return;
    }

    // Group skills by category
    const categories = {};
    result.data.forEach(skill => {
      const cat = skill.category || "General";
      if (!categories[cat]) categories[cat] = [];
      categories[cat].push(skill);
    });

    // Clear loading state
    container.innerHTML = "";

    // Render grouped categories safely
    Object.keys(categories).forEach(catName => {
      const card = document.createElement("div");
      card.className = "skill-category-card card";

      const title = document.createElement("h3");
      title.className = "skill-category-title";
      title.textContent = catName;
      card.appendChild(title);

      const badgeWrapper = document.createElement("div");
      badgeWrapper.className = "skill-badges-wrapper";

      categories[catName].forEach(skill => {
        const pill = document.createElement("span");
        pill.className = "skill-pill";
        // textContent prevents any XSS injection
        pill.textContent = skill.name;
        badgeWrapper.appendChild(pill);
      });

      card.appendChild(badgeWrapper);
      container.appendChild(card);
    });

  } catch (err) {
    console.error("Failed to load skills:", err);
    container.innerHTML = `
      <div class="error-state">
        <p>⚠️ Failed to load skills from server. Please refresh the page.</p>
      </div>`;
  }
}

/* --------------------------------------------------------------------------
   5. Dynamic Projects Loading (GET /api/projects)
   -------------------------------------------------------------------------- */
async function loadProjects() {
  const container = document.getElementById("projects-container");
  if (!container) return;

  try {
    const response = await fetch("/api/projects");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();

    if (!result.data || result.data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No projects recorded in database yet.</p>
        </div>`;
      return;
    }

    container.innerHTML = "";

    result.data.forEach(proj => {
      const card = document.createElement("div");
      card.className = "project-card card";

      const top = document.createElement("div");
      top.className = "project-top";

      // Header row: Title + Status Badge
      const headerRow = document.createElement("div");
      headerRow.className = "project-header-row";

      const title = document.createElement("h3");
      title.className = "project-title";
      title.textContent = proj.title;

      const badge = document.createElement("span");
      badge.className = "status-badge";
      badge.textContent = proj.status || "Planned / In Progress";

      headerRow.appendChild(title);
      headerRow.appendChild(badge);
      top.appendChild(headerRow);

      // Description
      const desc = document.createElement("p");
      desc.className = "project-desc";
      desc.textContent = proj.description;
      top.appendChild(desc);

      // Tech Stack
      const tech = document.createElement("div");
      tech.className = "project-tech";
      const techLabel = document.createElement("strong");
      techLabel.textContent = "Tech Stack: ";
      tech.appendChild(techLabel);
      tech.appendChild(document.createTextNode(proj.tech_stack));
      top.appendChild(tech);

      card.appendChild(top);

      // Honesty Rule: Only show action buttons if real URLs exist
      const hasGithub = Boolean(proj.github_url && proj.github_url.trim());
      const hasLive = Boolean(proj.live_url && proj.live_url.trim());
      const hasScreenshot = Boolean(proj.screenshot_url && proj.screenshot_url.trim());

      if (hasGithub || hasLive || hasScreenshot) {
        const actions = document.createElement("div");
        actions.className = "project-actions";

        if (hasLive) {
          const liveBtn = document.createElement("a");
          liveBtn.className = "btn btn-primary";
          liveBtn.href = proj.live_url;
          liveBtn.target = "_blank";
          liveBtn.rel = "noopener noreferrer";
          liveBtn.textContent = "Live Demo";
          actions.appendChild(liveBtn);
        }

        if (hasGithub) {
          const gitBtn = document.createElement("a");
          gitBtn.className = "btn btn-secondary";
          gitBtn.href = proj.github_url;
          gitBtn.target = "_blank";
          gitBtn.rel = "noopener noreferrer";
          gitBtn.textContent = "GitHub Code";
          actions.appendChild(gitBtn);
        }

        if (hasScreenshot) {
          const screenBtn = document.createElement("a");
          screenBtn.className = "btn btn-outline";
          screenBtn.href = proj.screenshot_url;
          screenBtn.target = "_blank";
          screenBtn.rel = "noopener noreferrer";
          screenBtn.textContent = "View Preview";
          actions.appendChild(screenBtn);
        }

        card.appendChild(actions);
      }

      container.appendChild(card);
    });

  } catch (err) {
    console.error("Failed to load projects:", err);
    container.innerHTML = `
      <div class="error-state">
        <p>⚠️ Failed to load projects from server. Please refresh the page.</p>
      </div>`;
  }
}

/* --------------------------------------------------------------------------
   6. Dynamic Certifications Loading (GET /api/certifications)
   -------------------------------------------------------------------------- */
async function loadCertifications() {
  const container = document.getElementById("certifications-container");
  if (!container) return;

  try {
    const response = await fetch("/api/certifications");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const result = await response.json();

    if (!result.data || result.data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No certifications recorded in database yet.</p>
        </div>`;
      return;
    }

    container.innerHTML = "";

    result.data.forEach(cert => {
      const card = document.createElement("div");
      card.className = "cert-card card";

      const title = document.createElement("h3");
      title.className = "cert-title";
      title.textContent = cert.title;
      card.appendChild(title);

      const issuer = document.createElement("p");
      issuer.className = "cert-issuer";
      issuer.textContent = cert.issuer;
      card.appendChild(issuer);

      const meta = document.createElement("div");
      meta.className = "cert-meta";
      meta.textContent = `Completed: ${cert.completion_date}`;
      card.appendChild(meta);

      // Honesty Rule: Only show link if certificate_url is present
      if (cert.certificate_url && cert.certificate_url.trim()) {
        const action = document.createElement("div");
        action.className = "cert-action";

        const link = document.createElement("a");
        link.className = "btn btn-outline";
        link.href = cert.certificate_url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "View Certificate";
        action.appendChild(link);

        card.appendChild(action);
      }

      container.appendChild(card);
    });

  } catch (err) {
    console.error("Failed to load certifications:", err);
    container.innerHTML = `
      <div class="error-state">
        <p>⚠️ Failed to load certifications from server. Please refresh the page.</p>
      </div>`;
  }
}

/* --------------------------------------------------------------------------
   7. Contact Form Handling & Validation (POST /api/contact)
   -------------------------------------------------------------------------- */
function initContactForm() {
  const form = document.getElementById("contact-form");
  const alertBox = document.getElementById("form-alert");
  const submitBtn = document.getElementById("contact-submit-btn");
  if (!form || !alertBox || !submitBtn) return;

  const btnText = submitBtn.querySelector(".btn-text");
  const btnSpinner = submitBtn.querySelector(".btn-spinner");

  // Input fields
  const nameInput = document.getElementById("contact-name");
  const emailInput = document.getElementById("contact-email");
  const subjectInput = document.getElementById("contact-subject");
  const messageInput = document.getElementById("contact-message");
  const honeypotInput = document.getElementById("form-website-url");

  // Error spans
  const nameError = document.getElementById("name-error");
  const emailError = document.getElementById("email-error");
  const subjectError = document.getElementById("subject-error");
  const messageError = document.getElementById("message-error");

  const emailRegex = /^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$/;

  function clearErrors() {
    [nameError, emailError, subjectError, messageError].forEach(span => {
      if (span) span.textContent = "";
    });
    [nameInput, emailInput, subjectInput, messageInput].forEach(inp => {
      if (inp) inp.classList.remove("is-invalid");
    });
    alertBox.style.display = "none";
    alertBox.className = "form-alert";
    alertBox.textContent = "";
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearErrors();

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const subject = subjectInput.value.trim();
    const message = messageInput.value.trim();
    const honeypot = honeypotInput ? honeypotInput.value.trim() : "";

    // Frontend Validations
    let hasError = false;

    if (!name || name.length < 2) {
      nameError.textContent = "Please enter your name (at least 2 characters).";
      nameInput.classList.add("is-invalid");
      hasError = true;
    }

    if (!email || !emailRegex.test(email)) {
      emailError.textContent = "Please enter a valid email address (e.g., name@example.com).";
      emailInput.classList.add("is-invalid");
      hasError = true;
    }

    if (!subject || subject.length < 2) {
      subjectError.textContent = "Please enter a subject (at least 2 characters).";
      subjectInput.classList.add("is-invalid");
      hasError = true;
    }

    if (!message || message.length < 10) {
      messageError.textContent = "Message must be at least 10 characters long.";
      messageInput.classList.add("is-invalid");
      hasError = true;
    }

    if (hasError) return;

    // Set UI to loading state
    submitBtn.disabled = true;
    btnText.textContent = "Sending Message...";
    btnSpinner.style.display = "inline-block";

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({
          name: name,
          email: email,
          subject: subject,
          message: message,
          website_url: honeypot
        })
      });

      const data = await response.json();

      if (response.ok && response.status === 201) {
        // Success state
        alertBox.className = "form-alert success";
        // Safe display using textContent
        alertBox.textContent = data.message || "Thank you! Your message has been sent successfully.";
        alertBox.style.display = "block";
        form.reset();
      } else {
        // Error state (400, 429, 500)
        alertBox.className = "form-alert error";
        alertBox.textContent = data.message || "An error occurred while submitting your message.";
        alertBox.style.display = "block";
      }
    } catch (networkErr) {
      console.error("Network error submitting contact form:", networkErr);
      alertBox.className = "form-alert error";
      alertBox.textContent = "Unable to reach server. Please check your network connection and try again.";
      alertBox.style.display = "block";
    } finally {
      // Restore UI state
      submitBtn.disabled = false;
      btnText.textContent = "Send Message";
      btnSpinner.style.display = "none";
    }
  });
}

/* --------------------------------------------------------------------------
   8. Dynamic Footer Year
   -------------------------------------------------------------------------- */
function updateFooterYear() {
  const yearSpan = document.getElementById("current-year");
  if (yearSpan) {
    yearSpan.textContent = String(new Date().getFullYear());
  }
}
