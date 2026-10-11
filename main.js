
const chatNavBtn = document.getElementById("chatNavBtn");              
const documentsNavBtn = document.getElementById("documentsNavBtn");
const chatPage = document.getElementById("chatPage");
const documentsPage = document.getElementById("documentsPage");
const pageTitle = document.getElementById("pageTitle");
const chatSubtitle = document.getElementById("chatSubtitle"); 
const filter = document.getElementById("sidebar-section"); 
const mainHeader = document.querySelector(".main-content > .header");

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
switchPage("chat"); // Mặc định mở trang chat


/* ==========================================
   DỮ LIỆU GIẢ LẬP
========================================== */

let documentGroups = [
    {
        name: "Quy định học bổng",
        files: [
            { name: "quy-dinh-hoc-bong.pdf", size: "PDF" },
            { name: "dieu-kien-hoc-bong.docx", size: "DOCX" }
        ],
        collapsed: false
    },
    {
        name: "Quy định tín chỉ",
        files: [
            { name: "quy-che-dao-tao.pdf", size: "PDF" }
        ],
        collapsed: false
    },
    {
        name: "Quy định học phí",
        files: [],
        collapsed: false
    }
];

const groupsList = document.getElementById("documentGroupsList");
const createGroupForm = document.getElementById("createGroupForm");
const newGroupName = document.getElementById("newGroupName"); // Nút tạo nhóm
const searchInput = document.getElementById("documentSearchInput"); // Nút tìm nhóm

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

function renderDocumentGroups() { // Hiển thị danh sách các nhóm tài liệu lên giao diện
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

createGroupForm.addEventListener("submit", event => {
    event.preventDefault();
    const name = newGroupName.value.trim();

    if (!name) {
        alert("Vui lòng nhập tên nhóm tài liệu.");
        newGroupName.focus();
        return;
    }

    const exists = documentGroups.some( group => group.name.toLowerCase() === name.toLowerCase()); // Kiểm tra tồn tại
        
    if (exists) {
        alert("Nhóm tài liệu này đã tồn tại.");
        return;
    }

    documentGroups.push({
        name,
        files: [],
        collapsed: false
    });

    newGroupName.value = "";
    searchInput.value = "";
    renderDocumentGroups();
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
   TẢI TỆP DEMO
========================================== */

groupsList.addEventListener("change", event => {
    const input = event.target; // Lấy phần tử phát sự kiện

    if (!input.matches(".document-upload-input")) return;

    const groupIndex = Number(input.dataset.group);
    const group = documentGroups[groupIndex];

    if (!group) return;

    const files = Array.from(input.files || []);
    const allowedExtensions = ["pdf", "docx", "txt"];
    let added = 0;

    files.forEach(file => {
        const extension = file.name.split(".").pop().toLowerCase();

        if (!allowedExtensions.includes(extension)) return;

        const exists = group.files.some(
            item => item.name.toLowerCase() === file.name.toLowerCase()
        );

        if (!exists) {
            group.files.push({
                name: file.name,
                size: extension.toUpperCase()
            });
            added++;
        }
    });

    if (added > 0) {
        alert(`Đã thêm ${added} tệp vào nhóm "${group.name}".`);
    } else {
        alert("Không có tệp mới hợp lệ được thêm.");
    }

    renderDocumentGroups();
});


/* Render dữ liệu mẫu ban đầu */
renderDocumentGroups();