(() => {
  const root = document.querySelector("[data-ai-chat]");
  if (!root) return;

  const form = root.querySelector("[data-chat-form]");
  const history = root.querySelector("[data-chat-history]");
  const questionField = form.querySelector("[name=question]");
  const errorBox = root.querySelector("[data-chat-error]");
  const submitButton = form.querySelector("[type=submit]");
  const maxHistoryMessages = 6;
  const maxHistoryContentLength = 500;
  let conversation = [];

  const appendMessage = (speaker, text) => {
    const item = document.createElement("div");
    item.className = "mb-3";
    const label = document.createElement("strong");
    label.textContent = speaker === "user" ? "Bạn" : "AI Assistant";
    const content = document.createElement("p");
    content.className = "mb-0 text-break";
    content.textContent = text;
    item.append(label, content);
    history.append(item);
    item.scrollIntoView({ block: "nearest" });
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = questionField.value.trim();
    if (!question) return;

    errorBox.textContent = "";
    appendMessage("user", question);
    questionField.value = "";
    questionField.disabled = true;
    submitButton.disabled = true;
    submitButton.textContent = "Đang trả lời…";

    try {
      const response = await fetch(root.dataset.endpoint, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: JSON.stringify({
          question,
          history: conversation.slice(-maxHistoryMessages).map(({ role, content }) => ({
            role,
            content: content.slice(0, maxHistoryContentLength),
          })),
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.message || "Không thể gửi câu hỏi lúc này.");
      appendMessage("assistant", payload.answer);
      conversation = [
        ...conversation,
        { role: "user", content: question },
        { role: "assistant", content: payload.answer },
      ].slice(-maxHistoryMessages);
    } catch (error) {
      errorBox.textContent = error.message || "Không thể gửi câu hỏi lúc này.";
    } finally {
      questionField.disabled = false;
      submitButton.disabled = false;
      submitButton.textContent = "Gửi";
      questionField.focus();
    }
  });
})();
