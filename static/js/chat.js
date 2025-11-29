(() => {
    const form = document.getElementById("message-form");
    if (!form) return;
    if (form.dataset.locked === "true") {
        return;
    }

    const history = document.getElementById("chat-history");
    const textarea = form.querySelector("textarea");
    const endpoint = form.dataset.endpoint;
    const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const cancelButton = document.getElementById("cancel-request");
    const fallbackInitials = "T";
    const fallbackName = "Tú";
    const assistantName = form.dataset.assistantName || "TrustAI";

    let controller = null;
    let typingMessage = null;

    const renderMessage = (role, content, timestamp, { markdown = false, html = null } = {}) => {
        const emptyState = history.querySelector(".empty-state");
        if (emptyState) {
            emptyState.remove();
        }
        const wrapper = document.createElement("div");
        wrapper.className = `chat-message chat-message-${role}`;
        wrapper.innerHTML = `
            <div class="chat-avatar">
                <span>${role === "user" ? (form.dataset.userInitials || fallbackInitials) : "AI"}</span>
            </div>
            <div class="chat-content">
                <div class="chat-meta">
                    <span class="chat-role">${role === "user" ? (form.dataset.userName || fallbackName) : assistantName}</span>
                    <span class="chat-timestamp">${timestamp}</span>
                </div>
                <div class="chat-text"></div>
            </div>
        `;
        const textContainer = wrapper.querySelector(".chat-text");
        if (html) {
            textContainer.innerHTML = html;
        } else if (markdown && window.renderTrustAIMarkdown) {
            textContainer.innerHTML = window.renderTrustAIMarkdown(content);
        } else {
            textContainer.textContent = content;
        }
        history.appendChild(wrapper);
        history.scrollTop = history.scrollHeight;
    };

    const showTypingIndicator = () => {
        if (typingMessage) {
            return;
        }
        const wrapper = document.createElement("div");
        wrapper.className = "chat-message chat-message-assistant chat-message-typing";
        wrapper.innerHTML = `
            <div class="chat-avatar">
                <span>AI</span>
            </div>
            <div class="chat-content">
                <div class="chat-meta">
                    <span class="chat-role">${assistantName}</span>
                    <span class="chat-timestamp">${nowTime()}</span>
                </div>
                <div class="chat-text typing-indicator">
                    <span class="typing-label">${assistantName} está pensando</span>
                    <span class="typing-dots"><span></span><span></span><span></span></span>
                </div>
            </div>
        `;
        history.appendChild(wrapper);
        history.scrollTop = history.scrollHeight;
        typingMessage = wrapper;
    };

    const hideTypingIndicator = () => {
        if (typingMessage) {
            typingMessage.remove();
            typingMessage = null;
        }
    };

    const setLoading = (isLoading) => {
        form.classList.toggle("is-loading", isLoading);
        form.querySelector("button[type='submit']").disabled = isLoading;
        if (cancelButton) {
            cancelButton.hidden = !isLoading;
            cancelButton.disabled = !isLoading;
        }
    };

    const nowTime = () => {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    };

    if (cancelButton) {
        cancelButton.addEventListener("click", () => {
            if (controller) {
                controller.abort();
            }
        });
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const content = textarea.value.trim();
        if (!content) {
            return;
        }

        if (controller) {
            controller.abort();
        }
        controller = new AbortController();
        const currentController = controller;

        renderMessage("user", content, nowTime());
        textarea.value = "";
        setLoading(true);

        try {
            showTypingIndicator();
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ content }),
                signal: currentController.signal,
            });

            const data = await response.json();
            if (!response.ok || !data.success) {
                const error = data.errors ? Object.values(data.errors).flat().join(" ") : "Error desconocido";
                hideTypingIndicator();
                renderMessage("assistant", `⚠️ ${error}`, nowTime());
                return;
            }

            const assistantTimestamp = new Date(data.assistant_message.created_at);
            const assistantTime = assistantTimestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
            hideTypingIndicator();
            renderMessage(
                "assistant",
                data.assistant_message.content,
                assistantTime,
                { markdown: true, html: data.assistant_message.content_html }
            );
        } catch (error) {
            hideTypingIndicator();
            if (error.name === "AbortError") {
                renderMessage("assistant", "⚠️ Solicitud cancelada por el usuario.", nowTime());
            } else {
                renderMessage("assistant", `⚠️ No se pudo contactar con ${assistantName}. Intenta nuevamente.`, nowTime());
            }
        } finally {
            if (controller === currentController) {
                controller = null;
            }
            hideTypingIndicator();
            setLoading(false);
        }
    });
})();
