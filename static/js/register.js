// Live validation on the sign-up form.
// This only helps the user: the server checks every rule again.

const form = document.getElementById("register-form");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirmInput = document.getElementById("confirm");

const emailHint = document.getElementById("email-hint");
const passwordHint = document.getElementById("password-hint");
const confirmHint = document.getElementById("confirm-hint");

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

// Show a message under a field and colour it green (ok) or red (bad).
function setHint(input, hint, ok, message) {
  hint.textContent = message;
  hint.classList.toggle("ok", ok);
  hint.classList.toggle("bad", !ok);
  input.classList.toggle("invalid", !ok);
}

function checkEmail() {
  const ok = EMAIL_RE.test(email.value.trim());
  setHint(email, emailHint, ok, ok ? "Looks good." : "Enter a valid email address.");
  return ok;
}

function checkPassword() {
  const remaining = 8 - password.value.length;
  const ok = remaining <= 0;
  setHint(password, passwordHint, ok,
    ok ? "Strong enough." : `${remaining} more character(s) needed.`);
  return ok;
}

function checkConfirm() {
  const ok = confirmInput.value !== "" && confirmInput.value === password.value;
  setHint(confirmInput, confirmHint, ok, ok ? "Passwords match." : "Passwords do not match.");
  return ok;
}

email.addEventListener("input", checkEmail);
password.addEventListener("input", () => {
  checkPassword();
  if (confirmInput.value) checkConfirm();
});
confirmInput.addEventListener("input", checkConfirm);

// Block the submit if a rule fails, so the user sees the problem right away.
form.addEventListener("submit", (event) => {
  const allOk = [checkEmail(), checkPassword(), checkConfirm()].every(Boolean);
  if (!allOk) event.preventDefault();
});
