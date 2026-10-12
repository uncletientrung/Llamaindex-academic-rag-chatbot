const chatNavBtn = document.getElementById("chatNavBtn");              
const documentsNavBtn = document.getElementById("documentsNavBtn");
const chatPage = document.getElementById("chatPage");
const documentsPage = document.getElementById("documentsPage");
const pageTitle = document.getElementById("pageTitle");
const chatSubtitle = document.getElementById("chatSubtitle"); 
// const filter = document.getElementById("sidebar-section"); 
const mainHeader = document.querySelector(".main-content > .header");
const questionInput = document.getElementById("questionInput"); // Ô nhập câu hỏi
const askBtn = document.getElementById("askBtn");       // Nút hỏi
const chatArea = document.getElementById("chatArea");   // Khung chat
const documentGroupSelect = document.getElementById("documentGroupSelect"); // combobox thư mục

const groupsList = document.getElementById("documentGroupsList");
const createGroupBtn = document.getElementById("createGroupBtn");
const newGroupName = document.getElementById("newGroupName"); // Nút tạo nhóm
const searchInput = document.getElementById("documentSearchInput"); // Nút tìm nhóm
let documentGroups = [];

const mainLoadingOverlay = document.getElementById("mainLoadingOverlay"); // Phần loading
const mainLoadingTitle =document.getElementById("mainLoadingTitle");
const mainLoadingMessage =document.getElementById("mainLoadingMessage");


// Địa chỉ backend FastAPI
const API_URL = "http://127.0.0.1:8000/chat";
const UPLOAD_API_URL = "http://127.0.0.1:8000/upload";
const DOCUMENTS_API_URL = "http://127.0.0.1:8000/documents";
const GROUPS_API_URL = "http://127.0.0.1:8000/groups";



// Bật/tắt nút gửi theo nội dung ô nhập
questionInput.addEventListener("input", () => {
    askBtn.disabled = !questionInput.value.trim();
});


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

chatNavBtn.addEventListener("click", (event) => {       // Chạy sự kiện khi ấn btn Chat
    event.preventDefault();
    switchPage("chat");
});

documentsNavBtn.addEventListener("click", (event) => { // Chạy sự kiện khi ấn btn document
    event.preventDefault();
    switchPage("documents");
});

const initialPage = documentsPage.style.display === "block" ? "documents" : "chat";
switchPage(initialPage);

/* ===================== Các hàm xử lý giao diện===================== */

function showMainLoading(title = "Đang tải dữ liệu",  message = "Vui lòng chờ trong giây lát...") {
    mainLoadingTitle.textContent = title;
    mainLoadingMessage.textContent = message;
    mainLoadingOverlay.style.display = "flex";
}

function hideMainLoading() {
    mainLoadingOverlay.style.display = "none";
}

function escapeHTML(value) { // Chống xss
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function getFileIcon(filename) { // Lấy icon by đuôi file
    const ext = filename.split(".").pop().toLowerCase();
    if (ext === "pdf") {
        return { icon: "fa-file-pdf", className: "pdf" };
    }
    if (ext === "docx") {
        return { icon: "fa-file-word", className: "docx" };
    }
    return { icon: "fa-file-alt", className: "txt" };
}

function updateDocumentStats() { // Thống kê tổng số tài liệu & số nhóm
    document.getElementById("totalGroups").textContent =
        documentGroups.length;

    document.getElementById("totalFiles").textContent =
        documentGroups.reduce((sum, group) => sum + group.files.length, 0);
}

function renderDocumentGroupSelect() {
    const selectedGroup = documentGroupSelect.value;
    documentGroupSelect.innerHTML = `
        <option value="">Tất cả tài liệu</option>
    `;
    documentGroups.forEach(group => {
        const option = document.createElement("option");
        option.value = group.name;
        option.textContent = group.name;
        documentGroupSelect.appendChild(option);
    });
    const groupExists = documentGroups.some(group => group.name === selectedGroup);     // Giữ lựa chọn cũ nếu nhóm vẫn còn
    documentGroupSelect.value = groupExists ? selectedGroup : "";
}

/* ==========================================
   Tải danh sách thư mục
========================================== */
async function loadDocumentGroups() { // Load document group từ thư mục data
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
        console.log(documentGroups)
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


function renderDocumentGroups() { // Hiển thị danh sách các nhóm tài liệu lên giao diện
    console.log(documentGroups)
    const keyword = searchInput.value.trim().toLowerCase();

    const filteredGroups = documentGroups
        .map((group, index) => ({ ...group, originalIndex: index }))
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

        const filesHTML = group.files.length    // Danh sách các file trong nhóm tài liệu
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


/* ==========================================
   TẠO NHÓM
========================================== */
createGroupBtn.addEventListener("click", async () => {
    const name = newGroupName.value.trim();
    if (!name) {
        alert("Vui lòng nhập tên nhóm tài liệu.");
        newGroupName.focus();
        return;
    }

    const exists = documentGroups.some(group => group.name.toLowerCase() === name.toLowerCase());
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
});


/* ==========================================
   TÌM KIẾM NHÓM
========================================== */

searchInput.addEventListener("input", renderDocumentGroups);


/* ==========================================
   THU GỌN / XÓA NHÓM / XÓA TỆP
========================================== */
groupsList.addEventListener("click", event => { // Lắng nghe sự kiện khi ấn bất kì vào chỗ nào ở groupList
    const button = event.target.closest("[data-action]");
    if (!button) return;

    const groupIndex = Number(button.dataset.group); // button.dataset.group LÀ LẤY data-group="0"
    const action = button.dataset.action;

    if (!documentGroups[groupIndex]) return;

    if (action === "toggle") { // Đóng mở nhóm
        documentGroups[groupIndex].collapsed =  !documentGroups[groupIndex].collapsed;
        renderDocumentGroups();
    }

    if (action === "delete-file") { // Xóa file
        const fileIndex = Number(button.dataset.file);
        const file = documentGroups[groupIndex].files[fileIndex];

        if (!file) return;

        if (confirm(`Bạn có muốn xóa tệp "${file.name}" không?`)) {
            documentGroups[groupIndex].files.splice(fileIndex, 1);
            renderDocumentGroups();
        }
    }

    if (action === "delete-group") { // Xóa group
        const group = documentGroups[groupIndex];

        if (confirm(`Bạn có muốn xóa nhóm "${group.name}" không?`)) {
            documentGroups.splice(groupIndex, 1);
            renderDocumentGroups();
        }
    }
});

/* ==========================================
   UPLOAD TÀI LIỆU THẬT
========================================== */
groupsList.addEventListener("change", async event => {
    const input = event.target;
    if (!input.matches(".document-upload-input")) return; // Không phải input upload tài liệu
    const groupIndex = Number(input.dataset.group);
    const group = documentGroups[groupIndex];
    if (!group) return;

    const files = Array.from(input.files || []);
    if (files.length === 0) return;
    const allowedExtensions = ["pdf", "docx", "txt"];
    showMainLoading( "Đang upload tài liệu", `Đang chuẩn bị ${files.length} tệp...`);
    // Upload từng file
    for (const file of files) {
        const extension = file.name.split(".").pop().toLowerCase();
        if (!allowedExtensions.includes(extension)) {// Kiểm tra định dạng
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
            console.log(`Upload thành công: ${file.name}` );  
        } catch (error) {
            console.error( `Lỗi upload ${file.name}:`,error);
            alert(`Không thể upload "${file.name}": ${error.message}` ); 
        }
    }

    // Xóa giá trị input để có thể chọn lại cùng file
    input.value = "";
    hideMainLoading();
    // Render lại giao diện
    await loadDocumentGroups();
});


/* Render dữ liệu mẫu ban đầu */
loadDocumentGroups();

///////////////////////////////////////////////////////////////////


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

// Gửi câu hỏi lên FastAPI
async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question || askBtn.disabled) return;
    appendMessage(question, "user");

    questionInput.value = "";
    askBtn.disabled = true;
    questionInput.disabled = true;

    // Hiển thị trạng thái đang xử lý
    const loadingMessage = appendMessage(
        "Đang tìm kiếm tài liệu và tạo câu trả lời...",
        "assistant"
    );

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Không thể xử lý câu hỏi."
            );
        }

        // Thay trạng thái chờ bằng câu trả lời thật
        loadingMessage.querySelector(".message-content").textContent =
            data.answer;

    } catch (error) {
        loadingMessage.querySelector(".message-content").textContent =
            "Lỗi: " + error.message;

        console.error("Lỗi gọi FastAPI:", error);
    } finally {
        questionInput.disabled = false;
        askBtn.disabled = !questionInput.value.trim();
        questionInput.focus();
    }
}

// Nhấn nút Gửi
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