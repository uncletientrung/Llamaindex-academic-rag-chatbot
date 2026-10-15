// ============================================================
// 1. KHAI BÁO DOM, BIẾN VÀ API
// ============================================================

// Các phần tử điều hướng và trang
const chatNavBtn = document.getElementById("chatNavBtn");
const documentsNavBtn = document.getElementById("documentsNavBtn");
const chatPage = document.getElementById("chatPage");
const documentsPage = document.getElementById("documentsPage");
const pageTitle = document.getElementById("pageTitle");
const chatSubtitle = document.getElementById("chatSubtitle");
const mainHeader = document.querySelector(".main-content > .header");

// Các phần tử giao diện Chat
const questionInput = document.getElementById("questionInput"); // Ô nhập câu hỏi
const askBtn = document.getElementById("askBtn"); // Nút hỏi
const chatArea = document.getElementById("chatArea"); // Khung chat
const documentGroupSelect = document.getElementById("documentGroupSelect"); // combobox thư mục

// Các phần tử giao diện quản lý tài liệu
const groupsList = document.getElementById("documentGroupsList");
const createGroupBtn = document.getElementById("createGroupBtn");
const newGroupName = document.getElementById("newGroupName"); // Nút tạo nhóm
const searchInput = document.getElementById("documentSearchInput"); // Nút tìm nhóm
let documentGroups = [];

// Các biến quản lý lịch sử chat
const historyList = document.getElementById("historyList");
const newChatBtn = document.getElementById("newChatBtn");
let conversations = [];
let currentConversationId = null;

// Các phần tử loading
const mainLoadingOverlay = document.getElementById("mainLoadingOverlay"); // Phần loading
const mainLoadingTitle = document.getElementById("mainLoadingTitle");
const mainLoadingMessage = document.getElementById("mainLoadingMessage");

// Các phần tử thông báo
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toastMessage");

// Địa chỉ backend FastAPI
const API_URL = "http://127.0.0.1:8000/chat";
const UPLOAD_API_URL = "http://127.0.0.1:8000/upload";
const DOCUMENTS_API_URL = "http://127.0.0.1:8000/documents";
const GROUPS_API_URL = "http://127.0.0.1:8000/groups";
const CONVERSATIONS_API_URL = "http://127.0.0.1:8000/conversations";


// ============================================================
// 2. CÁC HÀM TIỆN ÍCH VÀ XỬ LÝ GIAO DIỆN CHUNG
// ============================================================

// Hiển thị loading toàn màn hình
function showMainLoading(
    title = "Đang tải dữ liệu",
    message = "Vui lòng chờ trong giây lát..."
) {
    mainLoadingTitle.textContent = title;
    mainLoadingMessage.textContent = message;
    mainLoadingOverlay.style.display = "flex";
}

// Ẩn loading toàn màn hình
function hideMainLoading() {
    mainLoadingOverlay.style.display = "none";
}

// Chống XSS khi hiển thị dữ liệu dạng HTML
function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

// Lấy icon tương ứng với đuôi file
function getFileIcon(filename) {
    const ext = filename.split(".").pop().toLowerCase();

    if (ext === "pdf") {
        return { icon: "fa-file-pdf", className: "pdf" };
    }

    if (ext === "docx") {
        return { icon: "fa-file-word", className: "docx" };
    }

    return { icon: "fa-file-alt", className: "txt" };
}

// Hiển thị thông báo thành công hoặc thất bại
function showToast(message, type = "error") {
    const toast = document.getElementById("toast");
    const toastMessage = document.getElementById("toastMessage");

    toastMessage.textContent = message;

    // Có thể tùy chỉnh màu theo type sau này
    if (type === "success") {
        toast.style.background = "#28a745";
    } else {
        toast.style.background = "#dc3545"; // error mặc định
    }

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3500);
}

// Hiển thị hộp thoại xác nhận và trả về true/false
function confirmDialog(message) {
    return new Promise(resolve => {
        const dialog = document.getElementById("confirmDialog");
        const msg = document.getElementById("confirmMessage");
        const confirmBtn = document.getElementById("confirmBtn");
        const cancelBtn = document.getElementById("cancelBtn");

        msg.innerHTML = message;
        dialog.classList.add("show");

        // Click bên ngoài
        const handleOutsideClick = event => {
            if (event.target === dialog) {
                handleCancel();
            }
        };

        // Nhấn Esc
        const handleEsc = event => {
            if (event.key === "Escape") {
                handleCancel();
            }
        };

        const handleConfirm = () => {
            cleanup();
            resolve(true);
        };

        const handleCancel = () => {
            cleanup();
            resolve(false);
        };

        function cleanup() {
            dialog.classList.remove("show");
            confirmBtn.onclick = null;
            cancelBtn.onclick = null;
            dialog.onclick = null;
            document.removeEventListener("keydown", handleEsc);
        }

        confirmBtn.onclick = handleConfirm;
        cancelBtn.onclick = handleCancel;
        dialog.onclick = handleOutsideClick;
        document.addEventListener("keydown", handleEsc);
    });
}


// ============================================================
// 3. CHUYỂN ĐỔI TRANG CHAT / DOCUMENTS
// ============================================================

// Chuyển đổi giữa trang Chat và trang quản lý tài liệu
function switchPage(page) {
    const isDocuments = page === "documents";
    const mainContent = document.querySelector(".main-content");
    const sidebarRight = document.querySelector(".sidebar-right");

    chatPage.style.display = isDocuments ? "none" : "flex";
    mainHeader.style.display = isDocuments ? "none" : "flex";
    documentsPage.style.display = isDocuments ? "block" : "none"; // Tải ra trang documents

    // Ẩn sidebar phải và mở rộng nội dung chính
    sidebarRight.style.display = isDocuments ? "none" : "";
    mainContent.classList.toggle("documents-mode", isDocuments);

    // Cập nhật điều hướng
    chatNavBtn.classList.toggle("active", !isDocuments);
    documentsNavBtn.classList.toggle("active", isDocuments);

    // Ẩn bộ chọn nhóm tài liệu ở sidebar trái
    document.querySelector(".sidebar-section:nth-child(3)")
        ?.style.setProperty("display", isDocuments ? "none" : "flex");
}


// ============================================================
// 4. QUẢN LÝ NHÓM TÀI LIỆU VÀ HIỂN THỊ DANH SÁCH
// ============================================================

// Cập nhật thống kê tổng số nhóm và số tài liệu
function updateDocumentStats() {
    document.getElementById("totalGroups").textContent =
        documentGroups.length;

    document.getElementById("totalFiles").textContent =
        documentGroups.reduce((sum, group) => sum + group.files.length, 0);
}

// Cập nhật combobox chọn nhóm tài liệu
function renderDocumentGroupSelect() {
    const selectedGroup = documentGroupSelect.value;

    documentGroupSelect.innerHTML = `
        <option value="all">Tất cả tài liệu</option>
    `;

    documentGroups.forEach(group => {
        const option = document.createElement("option");
        option.value = group.name;
        option.textContent = group.name;
        documentGroupSelect.appendChild(option);
    });

    const groupExists = documentGroups.some(
        group => group.name === selectedGroup
    ); // Giữ lựa chọn cũ nếu nhóm vẫn còn

    documentGroupSelect.value = groupExists ? selectedGroup : "all";
}

// Tải danh sách nhóm và các tệp từ backend
async function loadDocumentGroups() {
    try {
        const response = await fetch(DOCUMENTS_API_URL);

        if (!response.ok) {
            throw new Error("Không thể tải danh sách tài liệu.");
        }

        const data = await response.json();

        documentGroups = data.groups.map(group => ({
            name: group.name,
            files: group.files.map(file => ({
                name: file.name,
                size: file.size,
                extension: file.extension,
                path: file.path
            })),
            collapsed: false
        }));

        console.log(documentGroups);

        renderDocumentGroups();
        renderDocumentGroupSelect();

    } catch (error) {
        console.error("Lỗi tải nhóm tài liệu:", error);

        groupsList.innerHTML = `
            <div class="document-empty-state">
                Không thể tải danh sách tài liệu từ máy chủ.
            </div>
        `;
    }
}

// Hiển thị danh sách nhóm, tệp và các nút thao tác
function renderDocumentGroups() {
    const keyword = searchInput.value.trim().toLowerCase();

    const filteredGroups = documentGroups
        .map((group, index) => ({
            ...group,
            originalIndex: index
        }))
        .filter(group => group.name.toLowerCase().includes(keyword));

    updateDocumentStats();

    if (filteredGroups.length === 0) {
        groupsList.innerHTML = `
            <div class="document-empty-state">
                <i class="fas fa-folder-open"></i>
                <span>Không tìm thấy nhóm tài liệu phù hợp.</span>
            </div>
        `;
        return;
    }

    groupsList.innerHTML = filteredGroups.map(group => {
        const index = group.originalIndex;

        const filesHTML = group.files.length
            ? group.files.map((file, fileIndex) => {
                const type = getFileIcon(file.name);

                return `
                    <div class="document-file-row">
                        <div class="file-icon ${type.className}">
                            <i class="fas ${type.icon}"></i>
                        </div>

                        <div class="file-info">
                            <span class="file-name">
                                ${escapeHTML(file.name)}
                            </span>

                            <span class="file-meta">
                                ${type.className.toUpperCase()} · Tài liệu demo
                            </span>
                        </div>

                        <button
                            class="btn-icon btn-delete-file"
                            data-action="delete-file"
                            data-group="${index}"
                            data-file="${fileIndex}"
                            title="Xóa tệp"
                            aria-label="Xóa tệp ${escapeHTML(file.name)}"
                        >
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                `;
            }).join("")
            : `
                <div class="document-empty-state">
                    <i class="fas fa-inbox"></i>
                    <span>Chưa có tài liệu trong nhóm này.</span>
                </div>
            `;

        return `
            <article class="document-group-card ${group.collapsed ? "collapsed" : ""}">
                <div class="document-group-header">
                    <div class="group-info">
                        <div class="group-folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>

                        <div>
                            <h4>${escapeHTML(group.name)}</h4>
                            <p>
                                <span class="group-file-count">
                                    ${group.files.length}
                                </span>
                                tài liệu
                            </p>
                        </div>
                    </div>

                    <div class="group-actions">
                        <button
                            class="btn-icon btn-toggle-group"
                            data-action="toggle"
                            data-group="${index}"
                            title="${group.collapsed ? "Mở rộng" : "Thu gọn"}"
                        >
                            <i class="fas fa-chevron-up"></i>
                        </button>

                        <button
                            class="btn-icon btn-delete-group"
                            data-action="delete-group"
                            data-group="${index}"
                            title="Xóa nhóm"
                        >
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>

                <div class="document-group-body">
                    <div class="group-file-list">
                        ${filesHTML}
                    </div>

                    <label class="document-upload-zone">
                        <i class="fas fa-cloud-upload-alt"></i>
                        <strong>Nhấn để chọn tài liệu</strong>
                        <span>
                            Hỗ trợ PDF, DOCX, TXT<br>
                            Có thể chọn nhiều tệp cùng lúc
                        </span>

                        <input
                            type="file"
                            class="document-upload-input"
                            data-group="${index}"
                            accept=".pdf,.docx,.txt"
                            multiple
                        >
                    </label>
                </div>
            </article>
        `;
    }).join("");
}

// Tạo nhóm tài liệu mới
async function createDocumentGroup() {
    const name = newGroupName.value.trim();

    if (!name) {
        alert("Vui lòng nhập tên nhóm tài liệu.");
        newGroupName.focus();
        return;
    }

    const exists = documentGroups.some(
        group => group.name.toLowerCase() === name.toLowerCase()
    );

    if (exists) {
        alert("Nhóm tài liệu này đã tồn tại.");
        return;
    }

    createGroupBtn.disabled = true;

    try {
        const response = await fetch(GROUPS_API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Không thể tạo nhóm tài liệu."
            );
        }

        newGroupName.value = "";
        searchInput.value = "";

        await loadDocumentGroups();

    } catch (error) {
        console.error("Lỗi tạo nhóm:", error);
        alert("Lỗi: " + error.message);

    } finally {
        createGroupBtn.disabled = false;
    }
}


// ============================================================
// 5. XỬ LÝ UPLOAD, XÓA NHÓM VÀ XÓA TỆP
// ============================================================

// Xử lý thu gọn nhóm, xóa nhóm hoặc xóa tệp
async function handleDocumentGroupClick(event) {
    const button = event.target.closest("[data-action]");
    if (!button) return;

    const groupIndex = Number(button.dataset.group); // button.dataset.group LÀ LẤY data-group="0"
    const action = button.dataset.action;
    const group = documentGroups[groupIndex];

    if (!group) return;

    if (action === "toggle") { // Đóng mở nhóm
        group.collapsed = !group.collapsed;
        renderDocumentGroups();
        return;
    }

    if (action === "delete-file") { // Xóa file
        const fileIndex = Number(button.dataset.file); // button.dataset.file LÀ LẤY data-file
        const file = group.files[fileIndex];

        if (!file) return;

        const ok = await confirmDialog(
            "Bạn có chắc muốn xóa tài liệu này?<br><small>Hành động này không thể hoàn tác.</small>"
        );

        if (!ok) return;

        showMainLoading(
            "Đang xóa tài liệu và cập nhật lại RAG",
            `Đang xóa ${file.name}`
        );

        try {
            const formData = new FormData();
            formData.append("group", group.name);
            formData.append("filename", file.name);

            const response = await fetch(
                `${DOCUMENTS_API_URL}/file`,
                {
                    method: "DELETE",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Không thể xóa file."
                );
            }

            showToast(
                `Xóa ${file.name} khỏi thư mục ${group.name} thành công!`,
                "success"
            );

            await loadDocumentGroups();

        } catch (error) {
            console.error("Lỗi xóa file:", error);
            alert("Lỗi: " + error.message);

        } finally {
            hideMainLoading();

            if (button.isConnected) {
                button.disabled = false;
            }
        }

        return;
    }

    if (action === "delete-group") {
        const ok = await confirmDialog(
            "Bạn có chắc muốn xóa tài liệu này?<br><small>Hành động này không thể hoàn tác.</small>"
        );

        if (!ok) return;

        showMainLoading(
            "Đang xóa nhóm tài liệu và cập nhật lại RAG",
            `Đang xóa thư mục ${group.name}`
        );

        try {
            const response = await fetch(
                `${GROUPS_API_URL}/${encodeURIComponent(group.name)}`,
                { method: "DELETE" }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Không thể xóa nhóm."
                );
            }

            showToast(
                `Xóa thư mục ${group.name} thành công!`,
                "success"
            );

            await loadDocumentGroups();

        } catch (error) {
            console.error("Lỗi xóa nhóm:", error);
            alert("Lỗi: " + error.message);

        } finally {
            hideMainLoading();

            if (button.isConnected) {
                button.disabled = false;
            }
        }
    }
}

// Upload các tệp được chọn vào nhóm tương ứng
async function handleDocumentUpload(event) {
    const input = event.target;

    if (!input.matches(".document-upload-input")) return; // Không phải input upload tài liệu

    const groupIndex = Number(input.dataset.group);
    const group = documentGroups[groupIndex];

    if (!group) return;

    const files = Array.from(input.files || []);
    if (files.length === 0) return;

    const allowedExtensions = ["pdf", "docx", "txt"];

    showMainLoading(
        "Đang upload tài liệu và cập nhật lại RAG",
        `Đang chuẩn bị ${files.length} tệp...`
    );

    // Upload từng file
    for (const file of files) {
        const extension = file.name.split(".").pop().toLowerCase();

        if (!allowedExtensions.includes(extension)) { // Kiểm tra định dạng
            alert(`File "${file.name}" không được hỗ trợ.`);
            continue;
        }

        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("group", group.name); // Gửi tên nhóm lên backend

            const response = await fetch( //Gửi file lên FastAPI
                UPLOAD_API_URL,
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Upload thất bại."
                );
            }

            showToast(`Upload thành công ${file.name}!`, "success");

        } catch (error) {
            console.error(`Lỗi upload ${file.name}:`, error);
            alert(`Không thể upload "${file.name}": ${error.message}`);
        }
    }

    // Xóa giá trị input để có thể chọn lại cùng file
    input.value = "";

    hideMainLoading();

    // Render lại giao diện
    await loadDocumentGroups();
}


// ============================================================
// 6. QUẢN LÝ LỊCH SỬ VÀ NỘI DUNG CUỘC TRÒ CHUYỆN
// ============================================================

// Tạo tin nhắn và hiển thị lên giao diện
function appendMessage(content, role) {
    const isUser = role === "user";

    const message = document.createElement("div");
    message.className = `message ${isUser ? "user" : "ai"}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.innerHTML = isUser
        ? '<i class="fas fa-user"></i>'
        : '<i class="fas fa-robot"></i>';

    const messageContent = document.createElement("div");
    messageContent.className = "message-content";
    messageContent.textContent = content;

    message.appendChild(avatar);
    message.appendChild(messageContent);

    chatArea.appendChild(message);
    chatArea.scrollTop = chatArea.scrollHeight;

    return message;
}

// Lấy danh sách cuộc trò chuyện từ FastAPI
async function loadConversations() {
    try {
        const response = await fetch(CONVERSATIONS_API_URL);

        if (!response.ok) {
            throw new Error("Không thể tải lịch sử chat.");
        }

        const data = await response.json();
        conversations = data.conversations || [];

        renderHistory();

    } catch (error) {
        console.error("Lỗi tải lịch sử chat:", error);

        historyList.innerHTML = `
            <p class="history-empty">
                Không thể tải lịch sử trò chuyện.
            </p>
        `;
    }
}

// Hiển thị danh sách cuộc trò chuyện ở sidebar bên phải
function renderHistory() {
    historyList.innerHTML = "";

    if (conversations.length === 0) {
        historyList.innerHTML = `
            <p class="history-empty">
                Chưa có lịch sử trò chuyện
            </p>
        `;
        return;
    }

    // Cuộc trò chuyện mới nhất hiển thị phía trên
    [...conversations].reverse().forEach(conversation => {
        const item = document.createElement("div");
        item.className = "history-item";

        if (conversation.conversation_id === currentConversationId) {
            item.classList.add("active");
        }

        const title = conversation.title?.trim() || "Cuộc trò chuyện mới";

        item.dataset.conversationId = conversation.conversation_id;

        item.innerHTML = `
            <div class="history-content">
                <i class="fas fa-comments"></i>

                <div class="history-text">
                    <div class="history-title"></div>
                </div>

                <button
                    class="delete-chat-btn"
                    data-action="delete-conversation"
                    title="Xóa cuộc trò chuyện"
                >
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;

        item.querySelector(".history-title").textContent =
            title.length > 25
                ? title.substring(0, 25) + "..."
                : title;

        historyList.appendChild(item);
    });
}

// Tải toàn bộ tin nhắn của một cuộc trò chuyện
async function loadConversation_Messages(conversationId) {
    try {
        showMainLoading(
            "Đang tải cuộc trò chuyện",
            "Đang tải lại lịch sử tin nhắn..."
        );

        const response = await fetch(
            `${CONVERSATIONS_API_URL}/${encodeURIComponent(conversationId)}`
        );

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));

            throw new Error(
                data.detail || "Không thể tải cuộc trò chuyện."
            );
        }

        const data = await response.json();

        currentConversationId = data.conversation_id; // Đặt lại id đoạn chat
        chatArea.innerHTML = "";

        // Hiển thị lại toàn bộ message
        for (const message of data.messages || []) {
            appendMessage(
                message.content,
                message.role
            );
        }

        // Cập nhật trạng thái active bên sidebar
        renderHistory();
        chatArea.scrollTop = chatArea.scrollHeight; // Scroll xuống cuối

    } catch (error) {
        console.error("Lỗi tải cuộc trò chuyện:", error);

        showToast(
            "Không thể tải lịch sử trò chuyện: " + error.message,
            "error"
        );

    } finally {
        hideMainLoading();
        questionInput.focus();
    }
}

// Xóa cuộc trò chuyện hiện tại và bắt đầu phiên mới
function startNewChat() {
    currentConversationId = null;
    chatArea.innerHTML = ""; // Xóa nội dung chat hiện tại

    // Reset ô nhập câu hỏi
    questionInput.value = "";
    questionInput.disabled = false;
    askBtn.disabled = true;

    documentGroupSelect.disabled = false; // Cho phép chọn nhóm tài liệu

    // Cập nhật trạng thái active trên sidebar
    renderHistory();
    questionInput.focus();
}

// Xử lý thao tác click vào lịch sử chat: mở hoặc xóa hội thoại
async function handleHistoryClick(event) {
    // XÓA CUỘC TRÒ CHUYỆN
    const deleteButton = event.target.closest(
        '[data-action="delete-conversation"]'
    );

    if (deleteButton) {
        event.stopPropagation();

        const historyItem = deleteButton.closest(".history-item");
        if (!historyItem) return;

        const conversationId = historyItem.dataset.conversationId;

        const conversation = conversations.find(
            item => String(item.conversation_id) === String(conversationId)
        );

        const title = conversation?.title?.trim() || "Cuộc trò chuyện này";

        const ok = await confirmDialog(
            `Bạn có chắc muốn xóa cuộc trò chuyện "<strong>${escapeHTML(title)}</strong>"?<br>
             <small>Toàn bộ tin nhắn trong cuộc trò chuyện sẽ bị xóa.</small>`
        );

        if (!ok) return;

        try {
            const response = await fetch(
                `${CONVERSATIONS_API_URL}/${encodeURIComponent(conversationId)}`,
                {
                    method: "DELETE"
                }
            );

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    data.detail || "Không thể xóa cuộc trò chuyện."
                );
            }

            // Nếu đang xóa conversation hiện tại
            if (String(currentConversationId) === String(conversationId)) {
                currentConversationId = null;
                chatArea.innerHTML = "";
            }

            showToast(
                "Đã xóa cuộc trò chuyện.",
                "success"
            );

            // Tải lại danh sách history
            await loadConversations();

        } catch (error) {
            console.error("Lỗi xóa cuộc trò chuyện:", error);

            showToast(
                "Không thể xóa cuộc trò chuyện: " + error.message,
                "error"
            );
        }

        return;
    }

    // CLICK VÀO CUỘC TRÒ CHUYỆN
    const historyItem = event.target.closest(".history-item");

    if (!historyItem) return;

    const conversationId = historyItem.dataset.conversationId;

    if (!conversationId) return;

    // Nếu click lại conversation đang mở thì không cần tải lại
    if (String(conversationId) === String(currentConversationId)) {
        return;
    }

    await loadConversation_Messages(conversationId);
}


// ============================================================
// 7. GỬI CÂU HỎI VÀ XỬ LÝ PHẢN HỒI STREAMING
// ============================================================

// Gửi câu hỏi lên FastAPI và hiển thị câu trả lời theo luồng streaming
async function sendQuestion() {
    const question = questionInput.value.trim();

    if (!question || askBtn.disabled) return;

    const selectedGroup = documentGroupSelect.value || "all";

    appendMessage(question, "user");

    questionInput.value = "";
    askBtn.disabled = true;
    questionInput.disabled = true;
    documentGroupSelect.disabled = true;

    // Hiển thị trạng thái đang xử lý
    const loadingMessage = appendMessage(
        "Đang tìm kiếm tài liệu và tạo câu trả lời...",
        "assistant"
    );

    const messageContent = loadingMessage.querySelector(".message-content");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                group: selectedGroup,
                conversation_id: currentConversationId
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));

            throw new Error(
                errorData.detail || "Không thể xử lý câu hỏi."
            );
        }

        // Backend trả ID qua header X-Conversation-ID
        const conversationId = response.headers.get("X-Conversation-ID");

        if (conversationId) {
            currentConversationId = conversationId;
            renderHistory();
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let isFirstChunk = true; // Dùng để kiểm tra đã có chunk đầu tiên chưa để xóa chữ đang tìm của Assistant
        let buffer = "";
        const STREAM_DELAY = 10; // Thời gian nghỉ giữa các lần hiển thị
        const CHARS_PER_STEP = 5; // Số ký tự hiển thị mỗi lần

        while (true) {
            const { value, done } = await reader.read();

            if (done) break; // Nếu stream đã kết thúc thì thoát vòng lặp

            // messageContent.textContent += decoder.decode(value, { stream: true});
            buffer += decoder.decode(value, {
                stream: true
            });

            if (isFirstChunk) {
                messageContent.textContent = "";
                isFirstChunk = false;
            }

            while (buffer.length > 0) {
                const chunk = buffer.slice(0, CHARS_PER_STEP);
                buffer = buffer.slice(CHARS_PER_STEP);

                messageContent.textContent += chunk;

                await new Promise(resolve => setTimeout(resolve, STREAM_DELAY));
            }
        }

        // Giải mã phần dữ liệu còn lại
        // messageContent.textContent += decoder.decode();
        const remainingText = decoder.decode();

        if (remainingText) {
            if (isFirstChunk) {
                messageContent.textContent = "";
            }

            messageContent.textContent += remainingText;
        }

        await loadConversations();

    } catch (error) {
        loadingMessage.querySelector(".message-content").textContent =
            "Lỗi: " + error.message;

        console.error("Lỗi gọi FastAPI:", error);

    } finally {
        questionInput.disabled = false;
        documentGroupSelect.disabled = false;
        askBtn.disabled = !questionInput.value.trim();
        questionInput.focus();
    }
}


// ============================================================
// 8. ĐĂNG KÝ TẤT CẢ SỰ KIỆN ADD EVENT LISTENER
// ============================================================

// Sự kiện nhập câu hỏi và bật/tắt nút gửi
questionInput.addEventListener("input", () => {
    askBtn.disabled = !questionInput.value.trim();
});

// Sự kiện chuyển đổi trang Chat / Documents
chatNavBtn.addEventListener("click", event => {
    event.preventDefault();
    switchPage("chat");
});

documentsNavBtn.addEventListener("click", event => {
    event.preventDefault();
    switchPage("documents");
});

// Sự kiện tạo nhóm tài liệu
createGroupBtn.addEventListener("click", createDocumentGroup);

// Sự kiện tìm kiếm nhóm tài liệu
searchInput.addEventListener("input", renderDocumentGroups);

// Sự kiện thu gọn nhóm, xóa nhóm và xóa tệp
groupsList.addEventListener("click", handleDocumentGroupClick);

// Sự kiện upload tài liệu
groupsList.addEventListener("change", handleDocumentUpload);

// Sự kiện bắt đầu cuộc trò chuyện mới
newChatBtn.addEventListener("click", startNewChat);

// Sự kiện gửi câu hỏi
askBtn.addEventListener("click", sendQuestion);

// Nhấn Enter để gửi câu hỏi
questionInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        event.preventDefault();

        if (!askBtn.disabled) {
            sendQuestion();
        }
    }
});

// Xử lý click vào lịch sử chat
historyList.addEventListener("click", handleHistoryClick);


// ============================================================
// 9. KHỞI TẠO VÀ TẢI DỮ LIỆU BAN ĐẦU
// ============================================================

// Khởi tạo trang mặc định
const initialPage =
    documentsPage.style.display === "block" ? "documents" : "chat";

switchPage(initialPage);

// Tải danh sách nhóm tài liệu ban đầu
loadDocumentGroups();

// Tải lịch sử cuộc trò chuyện ban đầu
loadConversations();